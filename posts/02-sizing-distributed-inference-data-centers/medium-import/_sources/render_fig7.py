"""
Figure 7 for Blog 1 v20. Operating-margin comparison across the six revenue
streams from Figure 6. Single horizontal bar per entity, no repeated AI-factory
row. AI factory is colored blue (same as Figure 6 token bars) to keep the
visual link; commodity streams are orange (same as Figure 6 commodity bars).
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

entities = [
    "AI factory (token sales)",
    "Large petrochem",
    "LNG terminal",
    "Ammonia / fertilizer",
    "Pharma API",
    "Large food processing",
]
# Operating-margin low-high ranges, in percent.
ranges = [
    (25, 45),  # AI factory (token sales) -- CoreWeave-anchored band
    (5, 15),   # Large petrochem
    (10, 25),  # LNG terminal
    (5, 20),   # Ammonia / fertilizer
    (10, 25),  # Pharma API
    (2, 6),    # Large food processing (meatpacking)
]

TOKEN_COLOR = "#3B78B8"
COMMODITY_COLOR = "#E8883A"
colors = [TOKEN_COLOR] + [COMMODITY_COLOR] * 5

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["font.size"] = 15

fig, ax = plt.subplots(figsize=(10.5, 5.2), dpi=140)

# Top of list at top of chart.
y_positions = np.arange(len(entities))[::-1]
bar_height = 0.58

for yp, (lo, hi), col in zip(y_positions, ranges, colors):
    width = hi - lo
    ax.barh(yp, width, left=lo, height=bar_height, color=col,
            edgecolor="#222222", linewidth=1.1, alpha=0.92)
    ax.text(hi + 1.2, yp, f"{lo}-{hi}%", va="center", ha="left",
            fontsize=14, color=col, weight="bold")

ax.set_yticks(y_positions)
ax.set_yticklabels(entities, fontsize=14)
ax.set_xlabel("Operating margin (%)", fontsize=15)
ax.set_xlim(0, 55)
ax.xaxis.grid(True, linestyle=":", color="#cccccc", linewidth=0.7)
ax.set_axisbelow(True)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.tick_params(axis="x", labelsize=13)

plt.subplots_adjust(left=0.28, right=0.96, top=0.96, bottom=0.13)

out_path = "/sessions/loving-jolly-bell/mnt/EnergyFlux/blog/_sources/blog1_fig7_margin.png"
plt.savefig(out_path, dpi=140, bbox_inches="tight", pad_inches=0.15,
            facecolor="white")
print(f"Wrote {out_path}")

import os
size = os.path.getsize(out_path)
print(f"File size: {size/1024:.0f} KB")
