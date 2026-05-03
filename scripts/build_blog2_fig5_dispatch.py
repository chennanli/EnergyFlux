"""
Blog 2 Figure 5 — Typical day dispatch profile for the default (40 MGD) archetype.

Shows over a 24-hour clear-sky day:
  - PV generation  (clear-sky cosine model, scaled to nameplate × CF)
  - WWTP baseline load (diurnal: peaks afternoon, valleys 02-05)
  - AI rack load (constant at facility level)
  - BESS state-of-charge (charges from PV surplus, discharges in evening)
  - Net grid import/export (residual)

This is illustrative — not an 8,760h simulation. Caption notes that.

Output: blog/_sources/blog2_fig5_dispatch.png
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "stage1_5_wwtp_dc"))

import matplotlib.pyplot as plt
import numpy as np
from design.archetypes import ARCHETYPES
from design.sizing import size_site


# ---- Get sizing for 40 MGD ----
result = size_site("wwtp_40mgd")
pv_kwp = result["pv"]["kwp"]              # 7,418 kWp
wwtp_avg_kw = result["site"]["wwtp_load_kw"]  # ~3,333 kW
ai_load_kw = result["dc"]["facility_load_mw"] * 1000.0  # ~3,250 kW
bess_kwh = result["bess"]["mwh"] * 1000.0  # 10,400 kWh
bess_max_charge_kw = result["bess"]["max_charge_kw"]
bess_max_discharge_kw = result["bess"]["max_discharge_kw"]


# ---- Hour grid: 24 hours, 15-minute resolution ----
dt_h = 0.25  # 15 min
hours = np.arange(0, 24, dt_h)
N = len(hours)


# ---- PV generation: clear-sky cosine model, 30°N, summer-ish ----
# Approximate sunrise 6am, sunset 8pm, peak at solar noon
sun_up = (hours >= 6.0) & (hours <= 20.0)
solar_angle = np.where(sun_up, np.cos((hours - 13.0) * np.pi / 14.0), 0.0)
solar_angle = np.maximum(solar_angle, 0.0)
# Scale so peak hits nameplate × performance ratio (about 0.85 × kWp)
pv_kw = pv_kwp * solar_angle * 0.85


# ---- WWTP baseline load: diurnal profile ----
# Average ~3,333 kW. Peaks afternoon (16h) about +30%, valleys at 04h about -25%.
diurnal = 1.0 + 0.30 * np.cos((hours - 16.0) * np.pi / 12.0)
diurnal = np.clip(diurnal, 0.75, 1.30)
wwtp_kw = wwtp_avg_kw * diurnal


# ---- AI rack load: constant at facility level (PUE-included) ----
ai_kw = np.full(N, ai_load_kw)


# ---- BESS dispatch (rule-based, illustrative) ----
# Strategy: when PV > (WWTP + AI), excess charges BESS. When PV < load, BESS discharges
# to cover the gap (up to its limits). Grid covers any remaining.
soc_kwh = np.zeros(N + 1)
soc_kwh[0] = bess_kwh * 0.50   # start at 50%
bess_charge_kw = np.zeros(N)
bess_discharge_kw = np.zeros(N)

soc_min = bess_kwh * 0.10
soc_max = bess_kwh * 0.90

eta_charge = 0.95
eta_discharge = 0.95

for i in range(N):
    surplus_kw = pv_kw[i] - (wwtp_kw[i] + ai_kw[i])
    if surplus_kw > 0:
        # Charge BESS
        room_kwh = soc_max - soc_kwh[i]
        max_charge_this_step = min(bess_max_charge_kw, surplus_kw, room_kwh / dt_h / eta_charge)
        bess_charge_kw[i] = max(0.0, max_charge_this_step)
        soc_kwh[i + 1] = soc_kwh[i] + bess_charge_kw[i] * dt_h * eta_charge
    else:
        # Discharge BESS to cover load
        deficit_kw = -surplus_kw
        avail_kwh = soc_kwh[i] - soc_min
        max_disch_this_step = min(bess_max_discharge_kw, deficit_kw, avail_kwh * eta_discharge / dt_h)
        bess_discharge_kw[i] = max(0.0, max_disch_this_step)
        soc_kwh[i + 1] = soc_kwh[i] - bess_discharge_kw[i] * dt_h / eta_discharge


# ---- Grid net (positive = import, negative = export) ----
grid_kw = (wwtp_kw + ai_kw) - pv_kw - bess_discharge_kw + bess_charge_kw


# ---- Plot ----
fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True,
                          gridspec_kw={"height_ratios": [3, 2, 2]})
fig.subplots_adjust(hspace=0.18, top=0.94, bottom=0.07, left=0.09, right=0.96)

BLUE = "#1F4E79"
GOLD = "#E8A33D"
GREEN = "#548235"
GREY = "#7F7F7F"
RED = "#C00000"
PURPLE = "#76448A"

# Panel A: power flows (kW)
ax = axes[0]
ax.fill_between(hours, 0, pv_kw, color=GOLD, alpha=0.5, label="PV generation")
ax.plot(hours, wwtp_kw, color=GREY, linewidth=2, label="WWTP baseline load")
ax.plot(hours, ai_kw, color=PURPLE, linewidth=2, linestyle="--", label="AI rack load")
ax.plot(hours, wwtp_kw + ai_kw, color=BLUE, linewidth=2.2, label="Total site load")
ax.set_ylabel("Power (kW)")
ax.set_title("(a) PV generation versus site load — 40 MGD archetype, clear-sky day at 30°N",
             fontsize=11, fontweight="bold", color=BLUE)
ax.legend(loc="upper left", fontsize=9, frameon=False, ncol=2)
ax.grid(True, linestyle="--", alpha=0.3)
ax.set_xlim(0, 24)
ax.set_ylim(bottom=0)

# Panel B: BESS dispatch and SOC
ax = axes[1]
ax.fill_between(hours, 0, bess_charge_kw, color=GREEN, alpha=0.5, label="BESS charging (kW)")
ax.fill_between(hours, 0, -bess_discharge_kw, color=RED, alpha=0.5,
                label="BESS discharging (kW)")
ax.set_ylabel("BESS power (kW)\n  ↑ charge / ↓ discharge")
ax.axhline(0, color="k", linewidth=0.5)
ax.legend(loc="upper left", fontsize=9, frameon=False)
ax.grid(True, linestyle="--", alpha=0.3)

ax2 = ax.twinx()
ax2.plot(hours, soc_kwh[:-1] / bess_kwh * 100, color=BLUE, linewidth=2.2,
         label="BESS state-of-charge (%)")
ax2.set_ylabel("SOC (%)", color=BLUE)
ax2.tick_params(axis="y", colors=BLUE)
ax2.set_ylim(0, 100)
ax.set_title("(b) BESS dispatch and state-of-charge", fontsize=11, fontweight="bold", color=BLUE)

# Panel C: grid net flow
ax = axes[2]
ax.fill_between(hours, 0, np.maximum(grid_kw, 0), color=BLUE, alpha=0.5,
                label="Grid import")
ax.fill_between(hours, 0, np.minimum(grid_kw, 0), color=GREEN, alpha=0.4,
                label="Grid export (PV surplus past BESS full)")
ax.axhline(0, color="k", linewidth=0.5)
ax.set_ylabel("Net grid power (kW)")
ax.set_xlabel("Hour of day (local solar time)")
ax.legend(loc="upper left", fontsize=9, frameon=False)
ax.grid(True, linestyle="--", alpha=0.3)
ax.set_title("(c) Net grid power — positive imports, negative exports",
             fontsize=11, fontweight="bold", color=BLUE)
ax.set_xticks(np.arange(0, 25, 3))


# ---- Save ----
out = os.path.join(os.path.dirname(__file__), "..", "blog", "_sources",
                   "blog2_fig5_dispatch.png")
fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
print(f"Saved {out}")
print(f"Image size: {os.path.getsize(out)} bytes")

# Print summary of the day
total_pv = np.sum(pv_kw) * dt_h
total_load = np.sum(wwtp_kw + ai_kw) * dt_h
total_grid_import = np.sum(np.maximum(grid_kw, 0)) * dt_h
total_grid_export = np.sum(-np.minimum(grid_kw, 0)) * dt_h
self_consumption_ratio = (total_pv - total_grid_export) / total_pv * 100 if total_pv > 0 else 0
print(f"\nClear-sky day energy balance:")
print(f"  Total PV gen:          {total_pv:>9.0f} kWh")
print(f"  Total site load:       {total_load:>9.0f} kWh")
print(f"  Grid import:           {total_grid_import:>9.0f} kWh")
print(f"  Grid export:           {total_grid_export:>9.0f} kWh")
print(f"  Self-consumption:      {self_consumption_ratio:>5.1f}%")
