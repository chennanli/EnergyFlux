"""Stage 1.5 Step 6 — Pandapower 5-bus 10kV network (PRD Part E).

Buses: grid (slack), pv, bess, wwtp, dc.
Lines: 10kV XLPE "NA2XS2Y 1x240 RM/25 6/10 kV".
Verify: voltages in [0.94, 1.06] pu, lines < 95% loading.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pandapower as pp


def create_network() -> pp.pandapowerNet:
    net = pp.create_empty_network()

    bus_grid = pp.create_bus(net, vn_kv=10.0, name="bus_grid")
    bus_pv = pp.create_bus(net, vn_kv=10.0, name="bus_pv")
    bus_bess = pp.create_bus(net, vn_kv=10.0, name="bus_bess")
    bus_wwtp = pp.create_bus(net, vn_kv=10.0, name="bus_wwtp")
    bus_dc = pp.create_bus(net, vn_kv=10.0, name="bus_dc")

    pp.create_ext_grid(net, bus=bus_grid, vm_pu=1.0, name="grid_connection")

    pp.create_line(net, bus_grid, bus_pv, length_km=0.3, std_type="NA2XS2Y 1x240 RM/25 6/10 kV", name="grid_pv")
    pp.create_line(net, bus_grid, bus_bess, length_km=0.1, std_type="NA2XS2Y 1x240 RM/25 6/10 kV", name="grid_bess")
    pp.create_line(net, bus_grid, bus_wwtp, length_km=0.5, std_type="NA2XS2Y 1x240 RM/25 6/10 kV", name="grid_wwtp")
    pp.create_line(net, bus_grid, bus_dc, length_km=0.2, std_type="NA2XS2Y 1x240 RM/25 6/10 kV", name="grid_dc")

    pp.create_sgen(net, bus=bus_pv, p_mw=0.0, q_mvar=0.0, name="pv_gen")
    pp.create_load(net, bus=bus_wwtp, p_mw=0.0, q_mvar=0.0, name="wwtp_load")
    pp.create_load(net, bus=bus_dc, p_mw=0.0, q_mvar=0.0, name="dc_load")
    pp.create_sgen(net, bus=bus_bess, p_mw=0.0, q_mvar=0.0, name="bess_gen")

    return net


def run_powerflow_annual(dispatch_csv: str | Path, output_csv: str | Path) -> pd.DataFrame:
    dispatch = pd.read_csv(dispatch_csv)
    net = create_network()

    records = []
    for i in range(len(dispatch)):
        row = dispatch.iloc[i]
        P_pv_mw = row["P_pv_kw"] / 1000.0
        P_wwtp_mw = row["P_wwtp_kw"] / 1000.0
        P_dc_mw = row["P_dc_kw"] / 1000.0
        P_bess_net_mw = (row["P_bess_dis_kw"] - row["P_bess_chg_kw"]) / 1000.0

        net.sgen.at[0, "p_mw"] = P_pv_mw
        net.sgen.at[1, "p_mw"] = P_bess_net_mw
        net.load.at[0, "p_mw"] = P_wwtp_mw
        net.load.at[1, "p_mw"] = P_dc_mw

        try:
            pp.runpp(net, numba=True)
            v = net.res_bus["vm_pu"].values
            line_loading = net.res_line["loading_percent"].max()
            records.append(
                {
                    "timestamp": row["timestamp"],
                    "v_bus_grid": v[0],
                    "v_bus_pv": v[1],
                    "v_bus_bess": v[2],
                    "v_bus_wwtp": v[3],
                    "v_bus_dc": v[4],
                    "max_line_loading_pct": line_loading,
                }
            )
        except Exception:
            records.append(
                {
                    "timestamp": row["timestamp"],
                    "v_bus_grid": np.nan,
                    "v_bus_pv": np.nan,
                    "v_bus_bess": np.nan,
                    "v_bus_wwtp": np.nan,
                    "v_bus_dc": np.nan,
                    "max_line_loading_pct": np.nan,
                }
            )

    df = pd.DataFrame(records)
    output_csv = Path(output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)
    return df


def verify_powerflow(df: pd.DataFrame) -> None:
    valid = df.dropna(subset=["v_bus_grid"])
    all_v = valid[["v_bus_grid", "v_bus_pv", "v_bus_bess", "v_bus_wwtp", "v_bus_dc"]]
    v_min = all_v.min().min()
    v_max = all_v.max().max()
    ll_max = valid["max_line_loading_pct"].max()
    pct_ok = (valid["max_line_loading_pct"] < 95).mean() * 100
    nan_pct = df["v_bus_grid"].isna().mean() * 100

    print("Step 6 verification:")
    print(f"  voltage range = [{v_min:.4f}, {v_max:.4f}] pu  (limit [0.94, 1.06])")
    print(f"  max line loading = {ll_max:.1f}%  (limit < 95% for >99% of hours)")
    print(f"  hours with loading < 95% = {pct_ok:.1f}%")
    print(f"  failed power flow hours = {nan_pct:.1f}%")

    assert v_min >= 0.94, f"voltage below 0.94 pu: {v_min:.4f}"
    assert v_max <= 1.06, f"voltage above 1.06 pu: {v_max:.4f}"
    assert pct_ok >= 99.0, f"line loading >95% too often: {pct_ok:.1f}%"
    print("  verification: PASS")


if __name__ == "__main__":
    here = Path(__file__).resolve().parent.parent
    df = run_powerflow_annual(
        here / "data" / "dispatch_hourly.csv",
        here / "data" / "powerflow_hourly.csv",
    )
    verify_powerflow(df)
