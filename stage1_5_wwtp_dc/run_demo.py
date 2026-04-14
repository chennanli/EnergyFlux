"""Stage 1.5 Step 9 — CLI runner for all 3 demo cases.

Usage: python run_demo.py [--case 1|2|3|all]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

sys.path.insert(0, str(ROOT))

from agent.dispatch_agent import DispatchAgent
from models.bess_dispatch import P_BIOGAS, dispatch_step
from models.dc_thermal import run_dc_simulation
from models.inference_load import P_DC_TOTAL_KW
from models.network_model import generate_network_scenario


def _load_annual_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    wwtp_path = DATA / "wwtp_load_hourly.csv"
    pv_path = DATA / "pv_hourly.csv"
    if not wwtp_path.exists():
        from models.wwtp_load_generator import generate_wwtp_load
        generate_wwtp_load(wwtp_path)
    if not pv_path.exists():
        from models.pv_generator import generate_pv_annual
        generate_pv_annual(pv_path)
    return pd.read_csv(wwtp_path), pd.read_csv(pv_path)


def _case_params(case: int) -> dict:
    if case == 1:
        return {
            "name": "Normal Operations (Sunny Weekday)",
            "start_hour": 24 * 104,  # mid-April
            "T_outside": None,
            "dc_load_scale": 0.7,
            "network_scenario": "normal",
            "wwtp_scale": 1.0,
        }
    elif case == 2:
        return {
            "name": "Thermal Stress + Grid Event",
            "start_hour": 24 * 196,  # mid-July
            "T_outside": 35.0,
            "dc_load_scale": 0.95,
            "network_scenario": "normal",
            "wwtp_scale": 1.4,  # storm event
        }
    else:
        return {
            "name": "Network Congestion → Routing Shift",
            "start_hour": 24 * 104,
            "T_outside": None,
            "dc_load_scale": 0.8,
            "network_scenario": "severe",
            "wwtp_scale": 1.0,
        }


def run_case(case_number: int, duration_hours: int = 24) -> pd.DataFrame:
    params = _case_params(case_number)
    print(f"\n{'='*60}")
    print(f"CASE {case_number}: {params['name']}")
    print(f"{'='*60}")

    wwtp_annual, pv_annual = _load_annual_data()
    start = params["start_hour"]
    end = min(start + duration_hours, len(wwtp_annual))

    wwtp_slice = wwtp_annual.iloc[start:end].reset_index(drop=True)
    pv_slice = pv_annual.iloc[start:end].reset_index(drop=True)
    n = len(wwtp_slice)

    wwtp_kw = wwtp_slice["P_total_kw"].values * params["wwtp_scale"]
    pv_kw = pv_slice["P_pv_kw"].values

    np.random.seed(42)
    # Flat DC load at case-specific utilization (physical basis: see
    # models/inference_load.py — a 24/7 inference Token Plant draws
    # near-constant power regardless of time of day).
    lf_scaled = np.full(n, float(params["dc_load_scale"]))
    dc_kw = lf_scaled * P_DC_TOTAL_KW

    if params["T_outside"] is not None:
        T_out = np.full(n, params["T_outside"])
    else:
        T_out = np.full(n, 15.0)
        for h in range(n):
            T_out[h] = 15.0 + 8.0 * np.sin(2 * np.pi * (h - 6) / 24)

    # Dispatch.
    SOC = 4000.0
    dispatch_records = []
    for i in range(n):
        t_hour = (start + i) % 24
        res = dispatch_step(t_hour, pv_kw[i], wwtp_kw[i], dc_kw[i], SOC)
        SOC = res["SOC_kwh"]
        dispatch_records.append(res)

    # DC thermal.
    df_thermal = run_dc_simulation(lf_scaled, T_out, dt_minutes=60)

    # Network.
    net_df = generate_network_scenario(
        params["network_scenario"], hours=n, steps_per_hour=1, seed=42
    )

    # Agent.
    agent = DispatchAgent()
    agent_records = []
    for i in range(n):
        d = dispatch_records[i]
        soc_pct = d["SOC_kwh"] / 7200 * 100
        r = agent.step(
            T_chip=df_thermal["T_chip_C"].iloc[i],
            soc_pct=soc_pct,
            P_pv=pv_kw[i],
            P_wwtp=wwtp_kw[i],
            P_grid=d["P_grid_kw"],
            api_latency=net_df["api_latency_ms"].iloc[i] if i < len(net_df) else 50,
            load_factor=lf_scaled[i],
            P_bess_chg=d["P_bess_chg_kw"],
            P_bess_dis=d["P_bess_dis_kw"],
            balance_error=d["balance_error_kw"],
        )
        agent_records.append(r)

    # Assemble results.
    timestamps = pd.date_range("2023-01-01", periods=n, freq="h")
    df = pd.DataFrame(
        {
            "timestamp": timestamps,
            "hour": [(start + i) % 24 for i in range(n)],
            "P_pv_kw": pv_kw,
            "P_wwtp_kw": wwtp_kw,
            "P_dc_kw": dc_kw,
            "P_bess_chg_kw": [r["P_bess_chg_kw"] for r in dispatch_records],
            "P_bess_dis_kw": [r["P_bess_dis_kw"] for r in dispatch_records],
            "P_grid_kw": [r["P_grid_kw"] for r in dispatch_records],
            "P_curtail_kw": [r["P_curtail_kw"] for r in dispatch_records],
            "SOC_kwh": [r["SOC_kwh"] for r in dispatch_records],
            "balance_error_kw": [r["balance_error_kw"] for r in dispatch_records],
            "T_chip_C": df_thermal["T_chip_C"].values,
            "T_coolant_C": df_thermal["T_coolant_C"].values,
            "load_factor_eff": df_thermal["load_factor_eff"].values,
            "T_outside_C": T_out,
            "api_latency_ms": net_df["api_latency_ms"].values[:n],
            "local_pct": net_df["local_pct"].values[:n],
            "routing": [r["routing"] for r in agent_records],
            "alert_level": [r["alert_level"] for r in agent_records],
            "reasoning": [r["reasoning"] for r in agent_records],
        }
    )

    outpath = DATA / f"case{case_number}_results.csv"
    df.to_csv(outpath, index=False)

    # Summary.
    max_err = df["balance_error_kw"].max()
    min_grid = df["P_grid_kw"].min()
    max_chg = df["P_bess_chg_kw"].max()
    max_dis = df["P_bess_dis_kw"].max()
    peak_chip = df["T_chip_C"].max()
    print(f"  max balance error = {max_err:.6f} kW")
    print(f"  min P_grid = {min_grid:.1f} kW")
    print(f"  BESS chg/dis max = {max_chg:.0f}/{max_dis:.0f} kW")
    print(f"  peak T_chip = {peak_chip:.1f}°C")
    print(f"  alerts: {sum(r['alert_level'] > 0 for r in agent_records)} / {n} hours")
    print(f"  saved → {outpath}")

    assert max_err < 0.001, f"balance error: {max_err}"
    assert min_grid >= -0.01, f"negative grid: {min_grid}"
    assert max_chg <= 1000.1, f"charge limit: {max_chg}"
    assert max_dis <= 2000.1, f"discharge limit: {max_dis}"
    print(f"  Case {case_number} verification: PASS")
    return df


def main():
    parser = argparse.ArgumentParser(description="Stage 1.5 WWTP-DC Demo Runner")
    parser.add_argument("--case", type=str, default="all", help="1, 2, 3, or all")
    args = parser.parse_args()

    cases = [1, 2, 3] if args.case == "all" else [int(args.case)]
    results = {}
    for c in cases:
        results[c] = run_case(c)

    print(f"\n{'='*60}")
    print("ALL CASES COMPLETE")
    print(f"{'='*60}")
    for c, df in results.items():
        print(f"  Case {c}: {len(df)} hours, max_err={df['balance_error_kw'].max():.6f} kW")


if __name__ == "__main__":
    main()
