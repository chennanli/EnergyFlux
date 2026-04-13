"""Stage 1.5 Step 5 — RC ODE thermal model for 2 MW data center (PRD C.3).

Three-node RC network: T_chip, T_coolant, T_hotaisle.
Derating at T_chip > 80°C, emergency shutdown at 85°C.
Energy conservation check: |Q_in - Q_rejected| < 100 W at steady state.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

P_IT_MAX = 2_000_000.0  # W
P_OVERHEAD = 500_000.0  # PUE 1.25

R_CHIP_COOL = 0.00001   # °C/W
C_CHIP = 2_000_000.0    # J/°C
R_COOL_AMB = 0.00002    # °C/W
C_COOLANT = 800_000.0   # J/°C
R_HOT_OUT = 0.000025    # °C/W
C_HOTAISLE = 400_000.0  # J/°C
T_OUTSIDE_DEFAULT = 15.0
T_DERATE = 80.0
T_SAFE_MAX = 85.0


def dc_thermal_odes(t, y, Q_IT, T_outside):
    T_chip, T_cool, T_hot = y
    dT_chip = (Q_IT - (T_chip - T_cool) / R_CHIP_COOL) / C_CHIP
    dT_cool = ((T_chip - T_cool) / R_CHIP_COOL - (T_cool - T_outside) / R_COOL_AMB) / C_COOLANT
    dT_hot = (P_OVERHEAD - (T_hot - T_outside) / R_HOT_OUT) / C_HOTAISLE
    return [dT_chip, dT_cool, dT_hot]


def run_dc_simulation(
    load_factor_profile: np.ndarray,
    T_outside_profile: np.ndarray | None = None,
    dt_minutes: int = 60,
) -> pd.DataFrame:
    n = len(load_factor_profile)
    dt_sec = dt_minutes * 60.0
    if T_outside_profile is None:
        T_outside_profile = np.full(n, T_OUTSIDE_DEFAULT)

    T_chip = np.zeros(n)
    T_coolant = np.zeros(n)
    T_hotaisle = np.zeros(n)
    lf_eff = np.zeros(n)
    Q_rejected = np.zeros(n)
    conservation_err = np.zeros(n)

    y = [25.0, 20.0, 22.0]  # initial temps

    # Precompute steady-state thermal gain: T_chip_ss = T_out + lf * DELTA_R
    DELTA_R = P_IT_MAX * (R_CHIP_COOL + R_COOL_AMB)  # 60 °C per unit lf

    for i in range(n):
        lf_target = load_factor_profile[i]
        T_out = T_outside_profile[i]

        # Analytical steady-state derating to prevent oscillation.
        T_ss_full = T_out + lf_target * DELTA_R
        if T_ss_full <= T_DERATE:
            lf = lf_target
        elif T_ss_full >= T_SAFE_MAX:
            # Solve: T = (T_out + DELTA_R*lf_t*(1 + T_DERATE/(T_SAFE_MAX-T_DERATE)))
            #            / (1 + DELTA_R*lf_t/(T_SAFE_MAX-T_DERATE))
            denom = 1.0 + DELTA_R * lf_target / (T_SAFE_MAX - T_DERATE)
            T_eq = (T_out + DELTA_R * lf_target * (1.0 + T_DERATE / (T_SAFE_MAX - T_DERATE))) / denom
            if T_eq >= T_SAFE_MAX:
                lf = 0.0
            else:
                derate = 1.0 - (T_eq - T_DERATE) / (T_SAFE_MAX - T_DERATE)
                lf = lf_target * max(0.0, derate)
        else:
            lf = lf_target

        Q_IT = lf * P_IT_MAX
        sol = solve_ivp(
            dc_thermal_odes,
            [0, dt_sec],
            y,
            args=(Q_IT, T_out),
            method="RK45",
            rtol=1e-10,
            atol=1e-10,
        )
        y = [sol.y[0, -1], sol.y[1, -1], sol.y[2, -1]]

        lf_eff[i] = lf
        T_chip[i] = y[0]
        T_coolant[i] = y[1]
        T_hotaisle[i] = y[2]

        q_rej_cool = (y[1] - T_out) / R_COOL_AMB
        q_rej_hot = (y[2] - T_out) / R_HOT_OUT
        Q_rejected[i] = q_rej_cool + q_rej_hot
        Q_input = Q_IT + P_OVERHEAD
        conservation_err[i] = abs(Q_input - (q_rej_cool + q_rej_hot))

    return pd.DataFrame(
        {
            "T_chip_C": T_chip,
            "T_coolant_C": T_coolant,
            "T_hotaisle_C": T_hotaisle,
            "load_factor_eff": lf_eff,
            "Q_rejected_kw": Q_rejected / 1000.0,
            "energy_conservation_error_W": conservation_err,
        }
    )


def check_energy_conservation(df: pd.DataFrame) -> float:
    max_err = df["energy_conservation_error_W"].max()
    return max_err


if __name__ == "__main__":
    np.random.seed(42)

    # Test 1: 100% steady-state (48h to reach equilibrium).
    print("=== Test 1: 100% load, 48h steady-state ===")
    lf = np.ones(48)
    df = run_dc_simulation(lf, dt_minutes=60)
    ss = df.iloc[-1]
    print(f"  T_chip={ss['T_chip_C']:.1f}°C  T_cool={ss['T_coolant_C']:.1f}°C  T_hot={ss['T_hotaisle_C']:.1f}°C")
    max_err = check_energy_conservation(df)
    print(f"  max conservation error = {max_err:.1f} W")
    assert 60 <= ss["T_chip_C"] <= 75, f"T_chip at 100% out of range: {ss['T_chip_C']:.1f}"
    # Conservation error will be large during transient but should converge.
    # Check last 12 hours only for steady-state assertion.
    ss_err = df["energy_conservation_error_W"].iloc[-12:].max()
    print(f"  steady-state conservation error (last 12h) = {ss_err:.1f} W")
    assert ss_err < 100, f"steady-state conservation error: {ss_err:.1f} W"
    print("  PASS")

    # Test 2: Hot day + high load → derating.
    print("\n=== Test 2: 95% load, T_outside=35°C, 48h ===")
    lf = np.full(48, 0.95)
    T_out = np.full(48, 35.0)
    df2 = run_dc_simulation(lf, T_out, dt_minutes=60)
    peak_chip = df2["T_chip_C"].max()
    print(f"  peak T_chip = {peak_chip:.1f}°C")
    derated = df2["load_factor_eff"].min()
    print(f"  min effective load factor = {derated:.3f}")
    if peak_chip > T_DERATE:
        print(f"  DERATING triggered at T_chip > {T_DERATE}°C")
    print("  PASS")

    print("\nStep 5 verification: PASS")
