"""
Power Flow Analysis — BESS Impact and Mitigation Strategies
============================================================
Compares overvoltage under different scenarios to demonstrate
the value of BESS placement and sizing for voltage regulation.

Scenarios:
  1. No BESS (baseline)
  2. BESS at busbar (current design, 50m from busbar)
  3. BESS co-located with PV (DC-coupled, same bus)
  4. Larger BESS co-located with PV (200kW/800kWh)

This analysis shows WHY BESS placement matters more than BESS sizing.
"""

import warnings
warnings.filterwarnings("ignore")
import os
os.environ["NUMBA_DISABLE_JIT"] = "1"

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
import numpy as np
import pandapower as pp
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

STAGE1_DIR    = Path(__file__).parent.parent
PV_CSV        = STAGE1_DIR / "data" / "processed" / "pv_comparison.csv"
PROCESSED_DIR = STAGE1_DIR / "data" / "processed"

# BESS parameters
BESS_EFF     = 0.95
BESS_SOC_MIN = 0.10
BESS_SOC_MAX = 0.90


def load_pv_and_profiles():
    """Load PV data and generate load profiles."""
    pv_df = pd.read_csv(PV_CSV, index_col=0)
    pv_df.index = pd.to_datetime(pv_df.index, utc=True)
    pv_col = "Bifacial + backtrack"
    if pv_col not in pv_df.columns:
        pv_col = pv_df.columns[-1]
    pv_kw = pv_df[pv_col].fillna(0).clip(lower=0)

    from stage1_solar_grid.grid.power_flow import generate_load_profiles
    load_profiles = generate_load_profiles(pv_kw.index)
    total_load_kw = load_profiles.sum(axis=1) * 1000

    return pv_kw, total_load_kw, load_profiles


def dispatch_bess(pv_kw, total_load_kw, bess_kw_max, bess_kwh):
    """Simple net-surplus BESS dispatch."""
    n = len(pv_kw)
    bess_kw = np.zeros(n)
    soc = np.zeros(n)
    soc[0] = 0.50
    eff = np.sqrt(BESS_EFF)

    for i in range(n):
        net_surplus = pv_kw.iloc[i] - total_load_kw.iloc[i]
        h = pv_kw.index[i].hour

        if net_surplus > 0 and soc[i] < BESS_SOC_MAX:
            charge = min(net_surplus, bess_kw_max, (BESS_SOC_MAX - soc[i]) * bess_kwh)
            bess_kw[i] = -charge
            if i + 1 < n:
                soc[i + 1] = soc[i] + (charge * eff) / bess_kwh
        elif 17 <= h <= 21 and soc[i] > BESS_SOC_MIN + 0.05:
            discharge = min(total_load_kw.iloc[i] * 0.4, bess_kw_max,
                          (soc[i] - BESS_SOC_MIN) * bess_kwh)
            bess_kw[i] = discharge
            if i + 1 < n:
                soc[i + 1] = soc[i] - (discharge / eff) / bess_kwh
        else:
            if i + 1 < n:
                soc[i + 1] = soc[i]

        if i + 1 < n:
            soc[i + 1] = np.clip(soc[i + 1], BESS_SOC_MIN, BESS_SOC_MAX)

    return pd.Series(bess_kw, index=pv_kw.index), pd.Series(soc, index=pv_kw.index)


def create_network(bess_at_pv=False):
    """Create network. If bess_at_pv=True, BESS is on PV bus (DC-coupled)."""
    net = pp.create_empty_network(name="Commercial Block — Fremont CA")

    bus_mv  = pp.create_bus(net, vn_kv=10,  name="MV Grid")
    bus_lv  = pp.create_bus(net, vn_kv=0.4, name="LV Busbar")
    bus_pv  = pp.create_bus(net, vn_kv=0.4, name="PV Plant")
    bus_bio = pp.create_bus(net, vn_kv=0.4, name="Biotech Lab")
    bus_off = pp.create_bus(net, vn_kv=0.4, name="Office Building")
    bus_ev  = pp.create_bus(net, vn_kv=0.4, name="EV Charging")

    pp.create_ext_grid(net, bus=bus_mv, vm_pu=1.02, name="Utility Grid")
    pp.create_transformer(net, hv_bus=bus_mv, lv_bus=bus_lv,
                          std_type="0.4 MVA 10/0.4 kV", name="Park Trafo")

    lv_line = "NAYY 4x120 SE"
    pp.create_line(net, bus_lv, bus_pv,  length_km=0.30, std_type=lv_line, name="Line PV")
    pp.create_line(net, bus_lv, bus_bio, length_km=0.20, std_type=lv_line, name="Line Biotech")
    pp.create_line(net, bus_lv, bus_off, length_km=0.15, std_type=lv_line, name="Line Office")
    pp.create_line(net, bus_lv, bus_ev,  length_km=0.25, std_type=lv_line, name="Line EV")

    # PV always on PV bus
    pp.create_sgen(net, bus=bus_pv, p_mw=0, q_mvar=0, name="PV Plant")

    # BESS placement depends on scenario
    if bess_at_pv:
        pp.create_sgen(net, bus=bus_pv, p_mw=0, q_mvar=0, name="BESS")  # co-located with PV
    else:
        bus_bess = pp.create_bus(net, vn_kv=0.4, name="BESS")
        pp.create_line(net, bus_lv, bus_bess, length_km=0.05, std_type=lv_line, name="Line BESS")
        pp.create_sgen(net, bus=bus_bess, p_mw=0, q_mvar=0, name="BESS")

    pp.create_load(net, bus=bus_bio, p_mw=0.050, q_mvar=0.010, name="Biotech Lab")
    pp.create_load(net, bus=bus_off, p_mw=0.030, q_mvar=0.005, name="Office Building")
    pp.create_load(net, bus=bus_ev,  p_mw=0.005, q_mvar=0.001, name="EV Charging")

    return net


def run_powerflow_timeseries(net, pv_kw, load_profiles, bess_kw):
    """Run power flow for all timesteps, return PV bus voltage."""
    n = len(pv_kw)
    v_pv = np.zeros(n)
    load_names = net.load["name"].tolist()
    pv_bus_idx = net.bus[net.bus["name"] == "PV Plant"].index[0]

    for i in range(n):
        net.sgen.at[0, "p_mw"] = pv_kw.iloc[i] / 1000
        net.sgen.at[1, "p_mw"] = bess_kw.iloc[i] / 1000

        for j, name in enumerate(load_names):
            if name in load_profiles.columns:
                net.load.at[j, "p_mw"] = load_profiles[name].iloc[i]
        try:
            pp.runpp(net, verbose=False)
            v_pv[i] = net.res_bus.at[pv_bus_idx, "vm_pu"]
        except:
            v_pv[i] = np.nan

    return pd.Series(v_pv, index=pv_kw.index)


def run_all_scenarios():
    """Run all 4 scenarios and compare."""
    pv_kw, total_load_kw, load_profiles = load_pv_and_profiles()
    print(f"PV peak: {pv_kw.max():.0f} kW, Load range: {total_load_kw.min():.0f}-{total_load_kw.max():.0f} kW")

    results = {}

    # Scenario 1: No BESS
    print("\n── Scenario 1: No BESS ──")
    net = create_network(bess_at_pv=False)
    no_bess = pd.Series(np.zeros(len(pv_kw)), index=pv_kw.index)
    v1 = run_powerflow_timeseries(net, pv_kw, load_profiles, no_bess)
    results["No BESS"] = v1
    print(f"  Overvoltage hours: {(v1 > 1.05).sum()}, Max: {v1.max():.4f} pu")

    # Scenario 2: BESS at busbar (current design)
    print("\n── Scenario 2: BESS at busbar (100kW/400kWh) ──")
    bess_kw, soc = dispatch_bess(pv_kw, total_load_kw, 100, 400)
    net = create_network(bess_at_pv=False)
    v2 = run_powerflow_timeseries(net, pv_kw, load_profiles, bess_kw)
    results["BESS at busbar\n100kW/400kWh"] = v2
    print(f"  Overvoltage hours: {(v2 > 1.05).sum()}, Max: {v2.max():.4f} pu")
    print(f"  BESS charged: {(-bess_kw[bess_kw<0]).sum()/1000:.0f} MWh")

    # Scenario 3: BESS co-located with PV (DC-coupled)
    print("\n── Scenario 3: BESS co-located with PV (100kW/400kWh, DC-coupled) ──")
    net = create_network(bess_at_pv=True)
    v3 = run_powerflow_timeseries(net, pv_kw, load_profiles, bess_kw)
    results["BESS at PV bus\n100kW/400kWh"] = v3
    print(f"  Overvoltage hours: {(v3 > 1.05).sum()}, Max: {v3.max():.4f} pu")

    # Scenario 4: Larger BESS co-located with PV
    print("\n── Scenario 4: Larger BESS at PV (200kW/800kWh, DC-coupled) ──")
    bess_kw_big, soc_big = dispatch_bess(pv_kw, total_load_kw, 200, 800)
    net = create_network(bess_at_pv=True)
    v4 = run_powerflow_timeseries(net, pv_kw, load_profiles, bess_kw_big)
    results["BESS at PV bus\n200kW/800kWh"] = v4
    print(f"  Overvoltage hours: {(v4 > 1.05).sum()}, Max: {v4.max():.4f} pu")
    print(f"  BESS charged: {(-bess_kw_big[bess_kw_big<0]).sum()/1000:.0f} MWh")

    return results, pv_kw, total_load_kw


def plot_comparison(results, pv_kw, total_load_kw):
    """Plot comparison of all scenarios."""
    fig = plt.figure(figsize=(16, 12))
    gs = gridspec.GridSpec(2, 2, hspace=0.35, wspace=0.30)
    colors = ["#E24B4A", "#888780", "#185FA5", "#1D9E75"]

    # Panel 1: Summer week voltage comparison
    ax1 = fig.add_subplot(gs[0, :])
    summer = slice("2022-06-21", "2022-06-27")
    for i, (label, v) in enumerate(results.items()):
        ax1.plot(v[summer].index, v[summer], label=label,
                 color=colors[i], linewidth=1.3, alpha=0.9)
    ax1.axhline(1.05, color="red", linewidth=1.5, linestyle="--", alpha=0.7, label="1.05 pu limit")
    ax1.set_title("PV Bus Voltage — Summer Week Comparison", fontsize=12)
    ax1.set_ylabel("Voltage (pu)")
    ax1.legend(fontsize=8, ncol=3)
    ax1.grid(True, alpha=0.2)

    # Panel 2: Annual overvoltage hours bar chart
    ax2 = fig.add_subplot(gs[1, 0])
    labels = list(results.keys())
    ov_hours = [(v > 1.05).sum() for v in results.values()]
    bars = ax2.bar(range(len(labels)), ov_hours, color=colors, alpha=0.85, width=0.6)
    for bar, val in zip(bars, ov_hours):
        ax2.text(bar.get_x() + bar.get_width()/2, val + 50,
                 f"{val:,}", ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax2.set_xticks(range(len(labels)))
    ax2.set_xticklabels(labels, fontsize=8)
    ax2.set_title("Overvoltage Hours (>1.05 pu) — 2 Years", fontsize=12)
    ax2.set_ylabel("Hours")
    ax2.grid(True, alpha=0.2, axis="y")

    # Panel 3: Max voltage bar chart
    ax3 = fig.add_subplot(gs[1, 1])
    max_v = [v.max() for v in results.values()]
    bars = ax3.bar(range(len(labels)), max_v, color=colors, alpha=0.85, width=0.6)
    ax3.axhline(1.05, color="red", linewidth=1.5, linestyle="--", alpha=0.7)
    for bar, val in zip(bars, max_v):
        ax3.text(bar.get_x() + bar.get_width()/2, val + 0.001,
                 f"{val:.3f}", ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax3.set_xticks(range(len(labels)))
    ax3.set_xticklabels(labels, fontsize=8)
    ax3.set_title("Peak Voltage at PV Bus", fontsize=12)
    ax3.set_ylabel("Voltage (pu)")
    ax3.set_ylim(1.04, 1.08)
    ax3.grid(True, alpha=0.2, axis="y")

    fig.suptitle("Power Flow Analysis — BESS Placement Impact on Voltage Regulation\n"
                 "Fremont CA | PV=185kWp | 0.4kV Distribution",
                 fontsize=13, fontweight="bold")

    out = PROCESSED_DIR / "powerflow_bess_comparison.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"\nPlot saved: {out}")
    plt.show()


if __name__ == "__main__":
    print("=" * 60)
    print("Power Flow Analysis — BESS Placement Comparison")
    print("=" * 60)

    results, pv_kw, total_load_kw = run_all_scenarios()

    # Summary table
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"{'Scenario':<35} {'OV Hours':>10} {'Max V':>10} {'Reduction':>12}")
    print("-" * 70)
    baseline = None
    for label, v in results.items():
        ov = (v > 1.05).sum()
        if baseline is None:
            baseline = ov
            pct = ""
        else:
            pct = f"-{(baseline-ov)/baseline*100:.1f}%"
        label_clean = label.replace('\n', ' ')
        print(f"{label_clean:<35} {ov:>10,} {v.max():>10.4f} {pct:>12}")

    plot_comparison(results, pv_kw, total_load_kw)
