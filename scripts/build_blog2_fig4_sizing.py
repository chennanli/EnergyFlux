"""
Blog 2 Figure 4 — Sizing comparison across 4 WWTP archetypes (30/40/50/60 MGD).

Side-by-side bars: PV kWp, BESS MWh, DC IT load MW, Peak grid demand kW.
Each archetype is one column.

Output: blog/_sources/blog2_fig4_sizing_comparison.png
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "stage1_5_wwtp_dc"))

import matplotlib.pyplot as plt
import numpy as np
from design.archetypes import ARCHETYPES
from design.sizing import size_site


# ---- Compute results ----
results = {k: size_site(k) for k in ARCHETYPES}
labels = ["30 MGD", "40 MGD", "50 MGD", "60 MGD"]
keys = ["wwtp_30mgd", "wwtp_40mgd", "wwtp_50mgd", "wwtp_60mgd"]

pv_kwp = [results[k]["pv"]["kwp"] for k in keys]
bess_mwh = [results[k]["bess"]["mwh"] for k in keys]
dc_mw = [results[k]["dc"]["facility_load_mw"] for k in keys]
racks = [results[k]["dc"]["racks"] for k in keys]
grid_peak_kw = [results[k]["grid"]["peak_added_kw"] for k in keys]
wwtp_kw = [results[k]["site"]["wwtp_load_kw"] for k in keys]


# ---- Build 2x2 panel chart ----
fig, axes = plt.subplots(2, 2, figsize=(11, 7.5))
fig.subplots_adjust(hspace=0.42, wspace=0.28, top=0.92, bottom=0.08, left=0.09, right=0.97)

BLUE = "#1F4E79"
GOLD = "#E8A33D"
GREY = "#7F7F7F"
GREEN = "#548235"

# Panel A: PV nameplate (kWp) and annual energy (MWh)
ax = axes[0, 0]
x = np.arange(len(labels))
w = 0.38
b1 = ax.bar(x - w / 2, pv_kwp, w, color=BLUE, label="PV nameplate (kWp)")
ax2 = ax.twinx()
b2 = ax2.bar(x + w / 2, [results[k]["pv"]["annual_mwh"] for k in keys], w, color=GOLD,
             label="Annual PV generation (MWh)")
ax.set_xticks(x); ax.set_xticklabels(labels)
ax.set_ylabel("PV nameplate (kWp)", color=BLUE)
ax2.set_ylabel("Annual generation (MWh)", color=GOLD)
ax.tick_params(axis="y", colors=BLUE)
ax2.tick_params(axis="y", colors=GOLD)
ax.set_title("(a) PV scale and annual energy", fontsize=11, fontweight="bold")
ax.grid(axis="y", linestyle="--", alpha=0.3)
for i, v in enumerate(pv_kwp):
    ax.text(i - w / 2, v * 1.02, f"{v:.0f}", ha="center", fontsize=8.5, color=BLUE)

# Panel B: BESS energy (MWh) and DC IT load (MW)
ax = axes[0, 1]
b1 = ax.bar(x - w / 2, bess_mwh, w, color=BLUE, label="BESS (MWh)")
ax2 = ax.twinx()
b2 = ax2.bar(x + w / 2, dc_mw, w, color=GREEN, label="DC facility load (MW)")
ax.set_xticks(x); ax.set_xticklabels(labels)
ax.set_ylabel("BESS energy (MWh, 4-hour)", color=BLUE)
ax2.set_ylabel("DC facility load (MW)", color=GREEN)
ax.tick_params(axis="y", colors=BLUE)
ax2.tick_params(axis="y", colors=GREEN)
ax.set_title("(b) BESS sizing and AI load", fontsize=11, fontweight="bold")
ax.grid(axis="y", linestyle="--", alpha=0.3)
for i, v in enumerate(bess_mwh):
    ax.text(i - w / 2, v * 1.02, f"{v:.1f}", ha="center", fontsize=8.5, color=BLUE)
for i, v in enumerate(dc_mw):
    ax2.text(i + w / 2, v * 1.02, f"{v:.2f}", ha="center", fontsize=8.5, color=GREEN)

# Panel C: WWTP existing load + AI added load → peak grid demand
ax = axes[1, 0]
ax.bar(x, wwtp_kw, w * 1.3, color=GREY, label="WWTP baseline load (kW)")
ax.bar(x, grid_peak_kw, w * 1.3, bottom=wwtp_kw, color=BLUE,
       label="Peak added grid demand (kW)")
ax.set_xticks(x); ax.set_xticklabels(labels)
ax.set_ylabel("Power (kW)")
ax.set_title("(c) Existing WWTP load + new peak grid demand", fontsize=11, fontweight="bold")
ax.legend(loc="upper left", fontsize=9, frameon=False)
ax.grid(axis="y", linestyle="--", alpha=0.3)
for i in range(len(labels)):
    total = wwtp_kw[i] + grid_peak_kw[i]
    ax.text(i, total * 1.02, f"{total:.0f}", ha="center", fontsize=8.5, color="black")

# Panel D: Rack count
ax = axes[1, 1]
ax.bar(x, racks, w * 1.3, color=BLUE)
ax.set_xticks(x); ax.set_xticklabels(labels)
ax.set_ylabel("GPU racks (Blackwell GB200 NVL72)")
ax.set_title("(d) GPU rack count per site", fontsize=11, fontweight="bold")
ax.grid(axis="y", linestyle="--", alpha=0.3)
for i, v in enumerate(racks):
    ax.text(i, v * 1.02, f"{v}", ha="center", fontsize=10, fontweight="bold", color=BLUE)

fig.suptitle("Sizing across four WWTP archetypes (Blackwell GB200 NVL72, 30°N, single-axis bifacial PV)",
             fontsize=12, fontweight="bold", color=BLUE, y=0.985)

# ---- Save ----
out = os.path.join(os.path.dirname(__file__), "..", "blog", "_sources",
                   "blog2_fig4_sizing_comparison.png")
fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
print(f"Saved {out}")
print(f"Image size: {os.path.getsize(out)} bytes")
