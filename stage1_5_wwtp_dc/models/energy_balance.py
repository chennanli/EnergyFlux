"""Stage 1.5 — Energy balance verification.

SOC bounds updated per Handoff Part 3.5: 10%-95% of 8,000 kWh = [800, 7600].
"""
from __future__ import annotations

import pandas as pd

SOC_MIN = 800.0   # 10% of 8,000 kWh
SOC_MAX = 7600.0  # 95% of 8,000 kWh


def verify_dispatch(df: pd.DataFrame) -> None:
    max_err = df["balance_error_kw"].max()
    min_grid = df["P_grid_kw"].min()
    min_soc = df["SOC_kwh"].min()
    max_soc = df["SOC_kwh"].max()
    max_chg = df["P_bess_chg_kw"].max()
    max_dis = df["P_bess_dis_kw"].max()

    print("Step 4 verification:")
    print(f"  max |balance_error| = {max_err:.6f} kW  (limit < 0.001)")
    print(f"  min P_grid          = {min_grid:.1f} kW  (must >= 0)")
    print(f"  SOC range           = [{min_soc:.0f}, {max_soc:.0f}] kWh  (limit [{SOC_MIN:.0f}, {SOC_MAX:.0f}])")
    print(f"  max P_bess_chg      = {max_chg:.1f} kW  (limit <= 1000)")
    print(f"  max P_bess_dis      = {max_dis:.1f} kW  (limit <= 2000)")

    assert max_err < 0.001, f"balance error {max_err}"
    assert min_grid >= -0.01, f"negative grid {min_grid}"
    assert min_soc >= SOC_MIN - 1, f"SOC below min {min_soc}"
    assert max_soc <= SOC_MAX + 1, f"SOC above max {max_soc}"
    assert max_chg <= 1000 + 0.1, f"charge exceeds limit {max_chg}"
    assert max_dis <= 2000 + 0.1, f"discharge exceeds limit {max_dis}"

    # Dispatch state distribution
    if "dispatch_state" in df.columns:
        states = df["dispatch_state"].value_counts()
        print(f"  dispatch states: {states.to_dict()}")

    print("  verification: PASS")
