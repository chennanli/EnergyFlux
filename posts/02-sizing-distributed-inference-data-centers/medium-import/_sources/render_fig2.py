"""
Figure 2 for Blog 1 v20.

Five-bar comparison:
  Bar 1 (orange): 2026 US AI DC in-construction, back-calculated from ~5 GW.
  Bar 2 (blue):   Distributed BTM model at 10% adoption across Table 3 categories.
  Bar 3 (blue):   Distributed BTM model at 30% adoption.
  Bar 4 (blue):   Distributed BTM model at 50% adoption.
  Bar 5 (orange): 2027 US AI DC in-construction, back-calculated from ~6.3 GW.

Units: Vera Rubin NVL72-equivalent racks (thousands).
DC bars are back-calculated estimates -- actual rack composition is not disclosed
by Sightline Climate's 2026 Data Center Outlook; we only know the aggregate
in-construction GW figure.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------
# VR NVL72 rack power range -- nameplate is ~190 kW IT; some estimates use
# ~230 kW to include cooling overhead, giving the lower bound on rack count.
RACK_KW_LOW = 190.0   # nameplate IT -> more racks per GW
RACK_KW_HIGH = 230.0  # with PUE overhead -> fewer racks per GW

# Sightline Climate 2026 Data Center Outlook, US in-construction capacity.
GW_2026 = 5.0
GW_2027 = 6.3

# 100% adoption total from Table 3 midpoints (racks).
TOTAL_100PCT = 38_500

# Adoption scenarios.
ADOPT_PCTS = [10, 30, 50]


def racks_from_gw(gw: float) -> tuple[float, float, float]:
    """Return (low, mid, high) rack count for a given GW, in thousands."""
    low = (gw * 1e6) / RACK_KW_HIGH / 1000.0
    high = (gw * 1e6) / RACK_KW_LOW / 1000.0
    mid = (low + high) / 2.0
    return low, mid, high


# ---------------------------------------------------------------------------
# Compute bar values (all in thousands of racks)
# ---------------------------------------------------------------------------
dc2026_low, dc2026_mid, dc2026_high = racks_from_gw(GW_2026)
dc2027_low, dc2027_mid, dc2027_high = racks_from_gw(GW_2027)

adopt_values = {p: (TOTAL_100PCT * p / 100.0) / 1000.0 for p in ADOPT_PCTS}

# Order the bars as specified by the user.
labels = [
    f"2026 US AI DC\nin-construction\n(~{GW_2026:.0f} GW)",
    "If adopt 10%",
    "If adopt 30%",
    "If adopt 50%",
    f"2027 US AI DC\nin-construction\n(~{GW_2027:.1f} GW)",
]
values = [
    dc2026_mid,
    adopt_values[10],
    adopt_values[30],
    adopt_values[50],
    dc2027_mid,
]

# Error bars: ranges only on the DC bars (back-calculation uncertainty).
err_low = [
    dc2026_mid - dc2026_low,
    0,
    0,
    0,
    dc2027_mid - dc2027_low,
]
err_high = [
    dc2026_high - dc2026_mid,
    0,
    0,
    0,
    dc2027_high - dc2027_mid,
]

# Colors (match existing figure palette).
DC_COLOR = "#E8883A"       # warm orange for data-center construction bars
MODEL_COLOR = "#3B78B8"    # blue for distributed-model adoption scenarios
colors = [DC_COLOR, MODEL_COLOR, MODEL_COLOR, MODEL_COLOR, DC_COLOR]

# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10.0, 5.8), dpi=160)

x = np.arange(len(labels))
bars = ax.bar(
    x,
    values,
    color=colors,
    edgecolor="#222222",
    linewidth=0.8,
    width=0.62,
)

# Error bars only on the two DC bars.
ax.errorbar(
    x,
    values,
    yerr=[err_low, err_high],
    fmt="none",
    ecolor="#444444",
    elinewidth=1.2,
    capsize=5,
)

# Value labels above each bar.
for i, (bar, val) in enumerate(zip(bars, values)):
    top = val + err_high[i]
    if i in (0, 4):
        # show range for DC bars
        if i == 0:
            text = f"{dc2026_mid:.1f}K\n({dc2026_low:.1f}–{dc2026_high:.1f}K)"
        else:
            text = f"{dc2027_mid:.1f}K\n({dc2027_low:.1f}–{dc2027_high:.1f}K)"
    else:
        text = f"{val:.2f}K"
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        top + 0.8,
        text,
        ha="center",
        va="bottom",
        fontsize=9.5,
        color="#222222",
    )

# Axes styling.
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=10)
ax.set_ylabel("Vera Rubin NVL72-equivalent racks (thousands)", fontsize=10.5)
ax.set_ylim(0, max(values + [v + e for v, e in zip(values, err_high)]) * 1.22)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.yaxis.grid(True, linestyle=":", color="#cccccc", linewidth=0.6)
ax.set_axisbelow(True)

ax.set_title(
    "Distributed BTM adoption scenarios vs. US AI DC capacity under construction",
    fontsize=12.5,
    pad=12,
    weight="bold",
)

# Subtitle / methodology note.
fig.text(
    0.5,
    0.905,
    "DC bars are back-calculated from public GW capacity figures "
    "(Sightline Climate 2026 Outlook); actual rack mix is not disclosed.\n"
    "Range bars reflect ~190–230 kW per rack. Adoption bars use Table 3 midpoints "
    "(~38.5K racks at 100% US adoption).",
    ha="center",
    va="top",
    fontsize=8.5,
    color="#555555",
    style="italic",
)

# Legend.
from matplotlib.patches import Patch

legend_handles = [
    Patch(facecolor=DC_COLOR, edgecolor="#222222",
          label="US AI DC capacity under construction (back-calculated from GW)"),
    Patch(facecolor=MODEL_COLOR, edgecolor="#222222",
          label="Distributed BTM model (this paper) at varying adoption rates"),
]
ax.legend(handles=legend_handles, loc="upper center", fontsize=9,
          frameon=False, ncol=1, bbox_to_anchor=(0.5, -0.18))

plt.tight_layout(rect=[0, 0.04, 1, 0.88])

out_path = "/sessions/loving-jolly-bell/mnt/EnergyFlux/blog/_sources/blog1_fig2_sitecount.png"
plt.savefig(out_path, dpi=160, bbox_inches="tight", facecolor="white")
print(f"Wrote {out_path}")

# Echo numbers for copy into caption.
print("\n-- Numbers --")
print(f"2026 DC: mid={dc2026_mid:.2f}K  range={dc2026_low:.2f}-{dc2026_high:.2f}K")
print(f"2027 DC: mid={dc2027_mid:.2f}K  range={dc2027_low:.2f}-{dc2027_high:.2f}K")
for p in ADOPT_PCTS:
    print(f"Adopt {p}%: {adopt_values[p]:.2f}K racks")
