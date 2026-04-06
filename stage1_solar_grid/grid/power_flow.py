"""
Sprint 4: Commercial Block Power Flow — Time-Series Simulation
================================================================
0.4kV commercial distribution network in Fremont, CA — a realistic
small commercial block with behind-the-meter PV + BESS.

Network topology:
  Utility Grid (10kV) → Trafo 400kVA (10kV/0.4kV) → LV Busbar
    ├── PV Plant (187 kWp / 156 kW AC)
    ├── BESS (100 kW / 400 kWh)
    ├── Biotech Lab (50 kW base 24/7, +10 kW daytime)
    └── Office Building (25 kW weekday daytime)

Total peak ~85 kW, off-peak ~52 kW
PV peak 135 kW >> load → significant surplus for BESS + overvoltage dynamics

Output:
  stage1_solar_grid/data/processed/powerflow_results.csv
  stage1_solar_grid/data/processed/powerflow_plot.png
"""

import pandas as pd
import numpy as np
import pandapower as pp
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings("ignore")
import os
os.environ["NUMBA_DISABLE_JIT"] = "1"  # suppress numba warnings

# ── Paths ─────────────────────────────────────────────────────────────────────
PV_CSV       = Path(__file__).parent.parent / "data" / "processed" / "pv_comparison.csv"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# ── BESS Parameters ──────────────────────────────────────────────────────────
BESS_KW      = 100     # max charge/discharge rate (kW)
BESS_KWH     = 400     # usable capacity (kWh)
BESS_EFF     = 0.95    # round-trip efficiency (one-way = sqrt)
BESS_SOC_MIN = 0.10    # minimum state of charge
BESS_SOC_MAX = 0.90    # maximum state of charge

# ── Voltage limits (ANSI C84.1 Range A) ──────────────────────────────────────
V_MIN = 0.95   # pu
V_MAX = 1.05   # pu


# ── Build network ────────────────────────────────────────────────────────────
def create_industrial_park():
    """
    Create a 0.4kV commercial block distribution network.

    Fremont CA commercial block: biotech lab, supermarket, EV chargers,
    medical clinic, office. 187 kWp PV + 100 kW BESS behind the meter.
    Total peak ~225 kW. PV can exceed midday load → overvoltage.
    """
    net = pp.create_empty_network(name="Commercial Block — Fremont CA")

    # Buses (0.4 kV LV distribution)
    bus_mv  = pp.create_bus(net, vn_kv=10,  name="MV Grid")
    bus_lv  = pp.create_bus(net, vn_kv=0.4, name="LV Busbar")
    bus_pv   = pp.create_bus(net, vn_kv=0.4, name="PV Plant")
    bus_bess = pp.create_bus(net, vn_kv=0.4, name="BESS")
    bus_bio  = pp.create_bus(net, vn_kv=0.4, name="Biotech Lab")
    bus_off  = pp.create_bus(net, vn_kv=0.4, name="Office Building")

    # External grid (MV side)
    pp.create_ext_grid(net, bus=bus_mv, vm_pu=1.02, name="Utility Grid")

    # Transformer 10kV / 0.4kV, 400 kVA (tight for ~250 kW load + 187 kWp PV)
    pp.create_transformer(net, hv_bus=bus_mv, lv_bus=bus_lv,
                          std_type="0.4 MVA 10/0.4 kV", name="Park Trafo")

    # LV cables (0.4kV NAYY — typical for commercial LV distribution)
    lv_line = "NAYY 4x120 SE"
    pp.create_line(net, bus_lv, bus_pv,   length_km=0.30, std_type=lv_line, name="Line PV")
    pp.create_line(net, bus_lv, bus_bess, length_km=0.05, std_type=lv_line, name="Line BESS")
    pp.create_line(net, bus_lv, bus_bio,  length_km=0.20, std_type=lv_line, name="Line Biotech")
    pp.create_line(net, bus_lv, bus_off,  length_km=0.15, std_type=lv_line, name="Line Office")

    # Static generators (PV and BESS — power updated each timestep)
    pp.create_sgen(net, bus=bus_pv,   p_mw=0, q_mvar=0, name="PV Plant")
    pp.create_sgen(net, bus=bus_bess, p_mw=0, q_mvar=0, name="BESS")

    # Loads — Fremont CA small commercial site
    # Total peak ~80 kW, off-peak ~45 kW
    # PV peak 135 kW >> load → clear surplus for BESS + overvoltage dynamics
    pp.create_load(net, bus=bus_bio, p_mw=0.050, q_mvar=0.010, name="Biotech Lab")
    pp.create_load(net, bus=bus_off, p_mw=0.025, q_mvar=0.004, name="Office Building")

    print(f"Network created: {len(net.bus)} buses, {len(net.line)} lines, "
          f"{len(net.load)} loads, {len(net.sgen)} generators")
    return net


# ── Load profiles (synthetic daily patterns) ─────────────────────────────────
def generate_load_profiles(index):
    """
    Generate hourly load profiles (MW) for a small commercial site.
    Biotech Lab (~50 kW 24/7) + Office (~25 kW daytime).
    Total peak ~80 kW. PV peak 135 kW → clear surplus for BESS charging.
    """
    hours = index.hour + index.minute / 60
    dow   = index.dayofweek
    is_weekday = dow < 5

    profiles = {}

    # Biotech Lab: 50 kW base 24/7 (lab equipment, cleanroom HVAC)
    # +10 kW daytime when staff present
    profiles["Biotech Lab"] = 0.050 + np.where(
        is_weekday & (hours >= 8) & (hours < 18), 0.010, 0.0)

    # Office Building: 25 kW weekdays 8am-7pm, near zero otherwise
    profiles["Office Building"] = np.where(
        is_weekday & (hours >= 8) & (hours < 19), 0.025, 0.002)

    return pd.DataFrame(profiles, index=index)


# ── BESS dispatch (simple rule-based) ────────────────────────────────────────
def dispatch_bess(pv_kw, total_load_kw):
    """
    BESS dispatch strategy:
      - Charge when PV > load (absorb excess to prevent overvoltage)
      - Discharge during evening peak 5-9pm (reduce grid import)
      - Also discharge if PV is zero and load is high

    Returns: bess_kw (positive = discharging/injecting, negative = charging)
             soc timeseries
    """
    n = len(pv_kw)
    bess_kw = np.zeros(n)
    soc = np.zeros(n)
    soc[0] = 0.50  # start at 50%
    eff = np.sqrt(BESS_EFF)  # one-way efficiency
    hours = pv_kw.index.hour

    for i in range(n):
        pv = pv_kw.iloc[i]
        h = hours[i]

        net_surplus = pv - total_load_kw.iloc[i]  # positive = PV exceeds load

        if net_surplus > 0 and soc[i] < BESS_SOC_MAX:
            # Net surplus → charge battery (absorb excess to prevent overvoltage)
            charge = min(net_surplus, BESS_KW)
            max_charge = (BESS_SOC_MAX - soc[i]) * BESS_KWH
            charge = min(charge, max_charge)
            bess_kw[i] = -charge  # negative = charging
            if i + 1 < n:
                soc[i + 1] = soc[i] + (charge * eff) / BESS_KWH
        elif 17 <= h <= 21 and soc[i] > BESS_SOC_MIN + 0.05:
            # Evening peak → discharge to supply load
            discharge = min(BESS_KW, total_load_kw.iloc[i] * 0.4)
            max_discharge = (soc[i] - BESS_SOC_MIN) * BESS_KWH
            discharge = min(discharge, max_discharge)
            bess_kw[i] = discharge
            if i + 1 < n:
                soc[i + 1] = soc[i] - (discharge / eff) / BESS_KWH
        else:
            bess_kw[i] = 0
            if i + 1 < n:
                soc[i + 1] = soc[i]

        if i + 1 < n:
            soc[i + 1] = np.clip(soc[i + 1], BESS_SOC_MIN, BESS_SOC_MAX)

    return pd.Series(bess_kw, index=pv_kw.index), pd.Series(soc, index=pv_kw.index)


# ── Time-series power flow ───────────────────────────────────────────────────
def run_timeseries_powerflow(net, pv_kw, load_profiles, bess_kw):
    """Run power flow for each timestep, collect bus voltages and line loading."""
    n = len(pv_kw)
    bus_names = net.bus["name"].tolist()
    n_buses = len(bus_names)
    n_lines = len(net.line)

    voltages = np.zeros((n, n_buses))
    line_loading = np.zeros((n, n_lines))

    load_names = net.load["name"].tolist()

    for i in range(n):
        # Update PV injection (negative load = generation)
        net.sgen.at[0, "p_mw"] = pv_kw.iloc[i] / 1000  # kW → MW

        # Update BESS injection
        net.sgen.at[1, "p_mw"] = bess_kw.iloc[i] / 1000  # kW → MW

        # Update loads
        for j, name in enumerate(load_names):
            if name in load_profiles.columns:
                net.load.at[j, "p_mw"] = load_profiles[name].iloc[i]

        # Run power flow
        try:
            pp.runpp(net, verbose=False)
            voltages[i] = net.res_bus["vm_pu"].values
            line_loading[i] = net.res_line["loading_percent"].values
        except pp.powerflow.LoadflowNotConverged:
            voltages[i] = np.nan
            line_loading[i] = np.nan

    voltage_df = pd.DataFrame(voltages, index=pv_kw.index, columns=bus_names)
    loading_df = pd.DataFrame(line_loading, index=pv_kw.index,
                              columns=net.line["name"].tolist())

    return voltage_df, loading_df


# ── Plot results ─────────────────────────────────────────────────────────────
def plot_results(pv_kw, load_profiles, bess_kw, soc, voltage_df, loading_df):
    """Generate 4-panel summary plot."""
    colors = {"PV": "#E24B4A", "BESS": "#1D9E75", "Load": "#185FA5",
              "Grid": "#888780", "Voltage": "#E24B4A"}

    # Pick summer week for detailed view
    summer = slice("2022-06-21", "2022-06-27")

    fig = plt.figure(figsize=(18, 14))
    gs = gridspec.GridSpec(3, 2, hspace=0.40, wspace=0.30)

    # ── Panel 1: Power balance (summer week) ──
    ax1 = fig.add_subplot(gs[0, :])
    total_load = load_profiles.sum(axis=1) * 1000  # MW → kW
    ax1.fill_between(pv_kw[summer].index, 0, total_load[summer],
                     alpha=0.3, color=colors["Load"], label="Total Load")
    ax1.plot(pv_kw[summer].index, pv_kw[summer], color=colors["PV"],
             linewidth=1.5, label="PV Generation")
    ax1.plot(bess_kw[summer].index, bess_kw[summer], color=colors["BESS"],
             linewidth=1.2, label="BESS (+=discharge, -=charge)")
    ax1.axhline(0, color="black", linewidth=0.5, alpha=0.3)
    ax1.set_title("Power Balance — Summer Week June 21-27", fontsize=11)
    ax1.set_ylabel("kW")
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.2)

    # ── Panel 2: Bus voltages (summer week) ──
    ax2 = fig.add_subplot(gs[1, 0])
    mv_buses = [c for c in voltage_df.columns if c not in ["HV Bus"]]
    for col in mv_buses:
        ax2.plot(voltage_df[summer].index, voltage_df[col][summer],
                 linewidth=0.8, alpha=0.7, label=col)
    ax2.axhline(V_MAX, color="red", linewidth=1, linestyle="--", alpha=0.6, label=f"V_max={V_MAX}")
    ax2.axhline(V_MIN, color="red", linewidth=1, linestyle="--", alpha=0.6, label=f"V_min={V_MIN}")
    ax2.set_title("Bus Voltages — Summer Week", fontsize=11)
    ax2.set_ylabel("Voltage (pu)")
    ax2.legend(fontsize=6, ncol=2)
    ax2.grid(True, alpha=0.2)

    # ── Panel 3: BESS SOC (summer week) ──
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.fill_between(soc[summer].index, 0, soc[summer] * 100,
                     alpha=0.4, color=colors["BESS"])
    ax3.plot(soc[summer].index, soc[summer] * 100, color=colors["BESS"], linewidth=1.2)
    ax3.axhline(BESS_SOC_MAX * 100, color="orange", linestyle="--", alpha=0.5, label=f"SOC max {BESS_SOC_MAX:.0%}")
    ax3.axhline(BESS_SOC_MIN * 100, color="orange", linestyle="--", alpha=0.5, label=f"SOC min {BESS_SOC_MIN:.0%}")
    ax3.set_title("BESS State of Charge — Summer Week", fontsize=11)
    ax3.set_ylabel("SOC (%)")
    ax3.set_ylim(0, 100)
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.2)

    # ── Panel 4: Line loading (summer week) ──
    ax4 = fig.add_subplot(gs[2, 0])
    for col in loading_df.columns:
        ax4.plot(loading_df[summer].index, loading_df[col][summer],
                 linewidth=0.8, alpha=0.7, label=col)
    ax4.axhline(80, color="red", linewidth=1, linestyle="--", alpha=0.6, label="80% limit")
    ax4.set_title("Line Loading — Summer Week", fontsize=11)
    ax4.set_ylabel("Loading (%)")
    ax4.legend(fontsize=6, ncol=2)
    ax4.grid(True, alpha=0.2)

    # ── Panel 5: Annual voltage statistics ──
    ax5 = fig.add_subplot(gs[2, 1])
    mv_voltages = voltage_df[mv_buses]
    monthly_max = mv_voltages.resample("ME").max().max(axis=1)
    monthly_min = mv_voltages.resample("ME").min().min(axis=1)
    months = monthly_max.index.strftime("%b %Y")
    x = range(len(months))
    ax5.fill_between(x, monthly_min.values, monthly_max.values,
                     alpha=0.3, color=colors["Voltage"])
    ax5.plot(x, monthly_max.values, color=colors["Voltage"], linewidth=1, label="Monthly max")
    ax5.plot(x, monthly_min.values, color=colors["Voltage"], linewidth=1, label="Monthly min")
    ax5.axhline(V_MAX, color="red", linewidth=1, linestyle="--", alpha=0.6)
    ax5.axhline(V_MIN, color="red", linewidth=1, linestyle="--", alpha=0.6)
    ax5.set_xticks(list(x))
    ax5.set_xticklabels(months, fontsize=7, rotation=45)
    ax5.set_title("Annual Voltage Envelope (all MV buses)", fontsize=11)
    ax5.set_ylabel("Voltage (pu)")
    ax5.legend(fontsize=9)
    ax5.grid(True, alpha=0.2)

    fig.suptitle("Industrial Park Power Flow — Fremont CA  |  "
                 f"PV=187kWp  |  BESS={BESS_KW}kW/{BESS_KWH}kWh  |  "
                 f"10kV Distribution", fontsize=13)

    out = PROCESSED_DIR / "powerflow_plot.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"\nPlot saved: {out}")
    plt.show()


# ── Print summary ────────────────────────────────────────────────────────────
def print_summary(voltage_df, loading_df, bess_kw, soc):
    """Print key statistics."""
    mv_buses = [c for c in voltage_df.columns if c not in ["HV Bus"]]
    mv_v = voltage_df[mv_buses]

    print("\n" + "=" * 60)
    print("POWER FLOW SUMMARY")
    print("=" * 60)

    print(f"\n── Voltage (ANSI C84.1: {V_MIN}-{V_MAX} pu) ──")
    print(f"  Overall min: {mv_v.min().min():.4f} pu ({mv_v.min().idxmin()})")
    print(f"  Overall max: {mv_v.max().max():.4f} pu ({mv_v.max().idxmax()})")

    v_low = (mv_v < V_MIN).any(axis=1).sum()
    v_high = (mv_v > V_MAX).any(axis=1).sum()
    print(f"  Hours below {V_MIN} pu: {v_low}")
    print(f"  Hours above {V_MAX} pu: {v_high}")

    if v_high > 0:
        worst_bus = mv_v.max().idxmax()
        print(f"  Worst overvoltage bus: {worst_bus} ({mv_v[worst_bus].max():.4f} pu)")

    print(f"\n── Line Loading ──")
    print(f"  Max loading: {loading_df.max().max():.1f}% ({loading_df.max().idxmax()})")
    overload_hours = (loading_df > 80).any(axis=1).sum()
    print(f"  Hours above 80%: {overload_hours}")

    print(f"\n── BESS ──")
    charge_kwh = (-bess_kw[bess_kw < 0]).sum()
    discharge_kwh = bess_kw[bess_kw > 0].sum()
    print(f"  Total charged:    {charge_kwh:.0f} kWh ({charge_kwh/1000:.1f} MWh)")
    print(f"  Total discharged: {discharge_kwh:.0f} kWh ({discharge_kwh/1000:.1f} MWh)")
    if charge_kwh > 0:
        print(f"  Round-trip eff:   {BESS_EFF*100:.0f}% (configured)")
    print(f"  SOC range:        {soc.min()*100:.0f}% - {soc.max()*100:.0f}%")
    print(f"  Cycles (approx):  {charge_kwh / BESS_KWH:.0f}")


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Load PV output from Sprint 3 (Mode 3: backtracking)
    pv_df = pd.read_csv(PV_CSV, index_col=0)
    pv_df.index = pd.to_datetime(pv_df.index, utc=True).tz_convert("America/Los_Angeles")
    pv_col = "1P tracker + backtrack"
    if pv_col not in pv_df.columns:
        pv_col = pv_df.columns[2]  # fallback to Mode 3 column
    pv_kw = pv_df[pv_col].fillna(0).clip(lower=0)
    print(f"PV data loaded: {len(pv_kw)} hours, peak={pv_kw.max():.0f} kW")

    # Generate synthetic load profiles
    load_profiles = generate_load_profiles(pv_kw.index)
    total_load_kw = load_profiles.sum(axis=1) * 1000  # MW → kW
    print(f"Load profiles generated: peak total = {total_load_kw.max():.0f} kW")

    # Dispatch BESS
    bess_kw, soc = dispatch_bess(pv_kw, total_load_kw)
    print(f"BESS dispatched: max charge={-bess_kw.min():.0f} kW, "
          f"max discharge={bess_kw.max():.0f} kW")

    # Create network
    net = create_industrial_park()

    # Run time-series power flow
    print(f"\nRunning power flow for {len(pv_kw)} timesteps...")
    voltage_df, loading_df = run_timeseries_powerflow(
        net, pv_kw, load_profiles, bess_kw)
    print("Power flow complete.")

    # Summary
    print_summary(voltage_df, loading_df, bess_kw, soc)

    # Save results
    results = pd.DataFrame({
        "pv_kw": pv_kw,
        "bess_kw": bess_kw,
        "soc": soc,
        "total_load_kw": total_load_kw,
    })
    for col in voltage_df.columns:
        results[f"v_{col}"] = voltage_df[col]
    out_csv = PROCESSED_DIR / "powerflow_results.csv"
    results.to_csv(out_csv)
    print(f"CSV saved: {out_csv}")

    # Plot
    plot_results(pv_kw, load_profiles, bess_kw, soc, voltage_df, loading_df)
