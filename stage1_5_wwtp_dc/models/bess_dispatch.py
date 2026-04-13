"""Stage 1.5 — TOU-aware BESS dispatch state machine (Handoff Part 3).

PG&E E-20 rate structure with 4-state summer dispatch + demand spike shaving.
Asymmetric: charge ≤ 1,000 kW (slow), discharge ≤ 2,000 kW (fast).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

# ── BESS physical parameters (from PRD) ─────────────────────────────────────
P_BESS_MAX_CHG = 1000.0   # kW — slow charge (prevents transformer overload)
P_BESS_MAX_DIS = 2000.0   # kW — fast discharge
E_CAPACITY = 8000.0        # kWh nameplate
SOC_MIN_KWH = E_CAPACITY * 0.10   # 800 kWh (10%)
SOC_MAX_KWH = E_CAPACITY * 0.95   # 7600 kWh (95%)
ETA = 0.9747               # sqrt(0.95)
P_BIOGAS = 800.0           # kW constant

# ── Dispatch targets (Handoff Part 3.5) ─────────────────────────────────────
NIGHT_CHARGE_TARGET = 0.60   # 60% SOC — leave room for solar top-up
ON_PEAK_READY_SOC = 0.85     # 85% SOC — minimum entering on-peak
DEMAND_THRESHOLD_KW = 4500.0 # kW — grid draw trigger for spike shaving

# ── PG&E E-20 rate structure (Handoff Part 3.1) ─────────────────────────────
SUMMER_MONTHS = {6, 7, 8, 9}


def _get_rate_period(hour: float, month: int, weekday: bool = True) -> str:
    """Return rate period: 'off_peak', 'partial_peak', or 'on_peak'."""
    if not weekday:
        return "off_peak"
    is_summer = month in SUMMER_MONTHS
    if hour < 8.5 or hour >= 21.5:
        return "off_peak"
    if is_summer and 12 <= hour < 18:
        return "on_peak"
    return "partial_peak"


def _tou_price(period: str) -> float:
    return {"off_peak": 0.07, "partial_peak": 0.12, "on_peak": 0.35}[period]


def dispatch_step(
    t_hour: int,
    P_pv: float,
    P_wwtp: float,
    P_dc: float,
    SOC: float,
    month: int = 4,
    weekday: bool = True,
) -> dict:
    """One-hour dispatch step using Part 3 state machine."""
    hour = float(t_hour)
    period = _get_rate_period(hour, month, weekday)
    soc_pct = SOC / E_CAPACITY

    P_bess_chg = 0.0
    P_bess_dis = 0.0
    state = ""

    # ── STATE 1: CHARGE (off-peak) ──────────────────────────────────────────
    if period == "off_peak":
        state = "CHARGE"
        target_kwh = NIGHT_CHARGE_TARGET * E_CAPACITY
        if SOC < target_kwh:
            P_bess_chg = min(P_BESS_MAX_CHG, (target_kwh - SOC) / ETA)
        # Also absorb any PV surplus (even at night, e.g. evening tail)
        surplus = max(0.0, P_pv + P_BIOGAS - P_wwtp - P_dc)
        if surplus > 0 and SOC < SOC_MAX_KWH:
            extra = min(P_BESS_MAX_CHG - P_bess_chg, surplus, (SOC_MAX_KWH - SOC) / ETA)
            P_bess_chg += max(0.0, extra)

    # ── STATE 2: HOLD + SOLAR ACCUMULATE (partial-peak morning) ─────────────
    elif period == "partial_peak" and hour < 12:
        state = "HOLD_SOLAR"
        # BESS does NOT discharge. PV charges battery toward 85%.
        surplus = max(0.0, P_pv + P_BIOGAS - P_wwtp - P_dc)
        target_kwh = ON_PEAK_READY_SOC * E_CAPACITY
        if surplus > 0 and SOC < target_kwh:
            P_bess_chg = min(P_BESS_MAX_CHG, surplus, (target_kwh - SOC) / ETA)

    # ── STATE 3A/3B: ON-PEAK (summer 12-6pm) ───────────────────────────────
    elif period == "on_peak":
        net_pv_for_dc = P_pv + P_BIOGAS - P_wwtp  # PV available after WWTP
        if net_pv_for_dc >= P_dc:
            # STATE 3A: Solar covers DC — BESS standby
            state = "SOLAR_COVERS"
            surplus = net_pv_for_dc - P_dc
            if surplus > 0 and SOC < SOC_MAX_KWH:
                P_bess_chg = min(P_BESS_MAX_CHG, surplus, (SOC_MAX_KWH - SOC) / ETA)
        else:
            # STATE 3B: Solar insufficient — BESS fills DC deficit
            state = "BESS_FILLS"
            deficit = P_dc - net_pv_for_dc
            if SOC > SOC_MIN_KWH:
                P_bess_dis = min(P_BESS_MAX_DIS, deficit, (SOC - SOC_MIN_KWH) * ETA)

    # ── STATE 2B: WINTER MIDDAY IDLE (partial-peak 12-6pm, no on-peak) ──────
    elif period == "partial_peak" and 12 <= hour < 18:
        # Intentional: winter has no on-peak window, so BESS stays idle midday.
        # Battery is preserved for demand spike shaving only (handled below).
        # PV surplus still charges if available.
        state = "WINTER_IDLE"
        surplus = max(0.0, P_pv + P_BIOGAS - P_wwtp - P_dc)
        if surplus > 0 and SOC < SOC_MAX_KWH:
            P_bess_chg = min(P_BESS_MAX_CHG, surplus, (SOC_MAX_KWH - SOC) / ETA)

    # ── STATE 4: DISCHARGE REMAINING (partial-peak evening) ─────────────────
    elif period == "partial_peak" and hour >= 18:
        state = "EVENING_DIS"
        # Discharge to supply DC, target SOC ~15-20% by 9:30pm
        if SOC > SOC_MIN_KWH:
            hours_left = max(1.0, 21.5 - hour)
            target_dis_rate = (SOC - SOC_MIN_KWH) / hours_left * ETA
            dc_deficit = max(0.0, P_dc - P_pv - P_BIOGAS + P_wwtp)
            P_bess_dis = min(P_BESS_MAX_DIS, target_dis_rate, dc_deficit + 500)

    # ── ENERGY BALANCE ──────────────────────────────────────────────────────
    P_grid_raw = P_wwtp + P_dc + P_bess_chg - P_pv - P_bess_dis - P_BIOGAS

    P_curtail = 0.0
    if P_grid_raw < 0:
        surplus = -P_grid_raw
        bess_headroom = max(0.0, min(P_BESS_MAX_CHG - P_bess_chg, (SOC_MAX_KWH - SOC) / 1.0))
        extra_chg = min(surplus, bess_headroom)
        P_bess_chg += extra_chg
        surplus -= extra_chg
        P_curtail = surplus
        P_grid = 0.0
    else:
        P_grid = P_grid_raw

    # ── DEMAND SPIKE SHAVING (Handoff Part 3.4) ────────────────────────────
    if P_grid > DEMAND_THRESHOLD_KW and SOC > SOC_MIN_KWH:
        spike = P_grid - DEMAND_THRESHOLD_KW
        shave = min(spike, P_BESS_MAX_DIS - P_bess_dis, (SOC - SOC_MIN_KWH) * ETA)
        P_bess_dis += shave
        P_grid -= shave
        if state:
            state += "+SPIKE_SHAVE"

    # ── SOC UPDATE ──────────────────────────────────────────────────────────
    SOC_new = SOC + P_bess_chg * ETA - P_bess_dis / ETA

    if SOC_new > SOC_MAX_KWH:
        excess = (SOC_new - SOC_MAX_KWH) / ETA
        P_bess_chg -= excess
        P_bess_chg = max(0.0, P_bess_chg)
        P_curtail += excess
        SOC_new = SOC + P_bess_chg * ETA - P_bess_dis / ETA
    if SOC_new < SOC_MIN_KWH:
        deficit = (SOC_MIN_KWH - SOC_new) * ETA
        P_bess_dis -= deficit
        P_bess_dis = max(0.0, P_bess_dis)
        SOC_new = SOC + P_bess_chg * ETA - P_bess_dis / ETA
        P_grid = max(0.0, P_wwtp + P_dc + P_bess_chg - P_pv - P_bess_dis - P_BIOGAS - P_curtail)

    balance_err = abs(
        (P_pv + P_bess_dis + P_grid + P_BIOGAS)
        - (P_wwtp + P_dc + P_bess_chg + P_curtail)
    )

    return {
        "P_bess_chg_kw": P_bess_chg,
        "P_bess_dis_kw": P_bess_dis,
        "P_grid_kw": P_grid,
        "P_curtail_kw": P_curtail,
        "SOC_kwh": SOC_new,
        "balance_error_kw": balance_err,
        "dispatch_state": state,
        "rate_period": period,
        "electricity_price": _tou_price(period),
    }


def run_annual_dispatch(
    wwtp_csv: str | Path,
    pv_csv: str | Path,
    output_csv: str | Path,
) -> pd.DataFrame:
    wwtp = pd.read_csv(wwtp_csv, parse_dates=["timestamp"])
    pv = pd.read_csv(pv_csv)
    from models.inference_load import generate_dc_load

    dc = generate_dc_load(hours=len(wwtp))

    records = []
    SOC = NIGHT_CHARGE_TARGET * E_CAPACITY  # start at night target

    for i in range(len(wwtp)):
        ts = wwtp["timestamp"].iloc[i]
        t_hour = i % 24
        month = pd.Timestamp(ts).month if isinstance(ts, str) else ts.month
        weekday = pd.Timestamp(ts).weekday() < 5 if isinstance(ts, str) else ts.weekday() < 5

        res = dispatch_step(
            t_hour=t_hour,
            P_pv=pv["P_pv_kw"].iloc[i],
            P_wwtp=wwtp["P_total_kw"].iloc[i],
            P_dc=dc["P_dc_kw"].iloc[i],
            SOC=SOC,
            month=month,
            weekday=weekday,
        )
        SOC = res["SOC_kwh"]
        records.append(
            {
                "timestamp": ts,
                "P_pv_kw": pv["P_pv_kw"].iloc[i],
                "P_wwtp_kw": wwtp["P_total_kw"].iloc[i],
                "P_dc_kw": dc["P_dc_kw"].iloc[i],
                "P_bess_chg_kw": res["P_bess_chg_kw"],
                "P_bess_dis_kw": res["P_bess_dis_kw"],
                "P_grid_kw": res["P_grid_kw"],
                "P_curtail_kw": res["P_curtail_kw"],
                "SOC_kwh": res["SOC_kwh"],
                "balance_error_kw": res["balance_error_kw"],
                "dispatch_state": res["dispatch_state"],
                "rate_period": res["rate_period"],
                "electricity_price": res["electricity_price"],
                "hour_of_day": t_hour,
            }
        )

    df = pd.DataFrame(records)
    output_csv = Path(output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)
    return df


if __name__ == "__main__":
    here = Path(__file__).resolve().parent.parent
    df = run_annual_dispatch(
        here / "data" / "wwtp_load_hourly.csv",
        here / "data" / "pv_hourly.csv",
        here / "data" / "dispatch_hourly.csv",
    )
    from models.energy_balance import verify_dispatch

    verify_dispatch(df)
