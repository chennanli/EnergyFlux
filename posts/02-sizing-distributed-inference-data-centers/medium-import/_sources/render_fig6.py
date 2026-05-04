"""
Figure 6 for Blog 1 v20 -- v4.

Single revenue chart only. Token margin is uniform ~25-45% across all
site types, so a bar panel for margin is information-free; the margin
comparison is done in a compact HTML table beneath the figure.

Fonts sized for body-text legibility at the 820px blog container width.
X-axis labels rotated ~30 deg so they breathe.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

# ---------------------------------------------------------------------------
# Data (annual revenue, USD millions, low/high)
# ---------------------------------------------------------------------------
sites = [
    "Large petrochem (grid-extended), 30-50 MW",
    "LNG terminal, ~40 MW",
    "Ammonia / fertilizer, ~10 MW",
    "Pharma API, ~4 MW",
    "Large food processing, ~2 MW",
]

token_rev = [(200, 800), (200, 600), (50, 150), (20, 60), (10, 30)]
commodity_rev = [(3000, 10000), (1000, 5000), (500, 2000), (500, 3000), (200, 1000)]

TOKEN_COLOR = "#3B78B8"
COMMODITY_COLOR = "#E8883A"

# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["font.size"] = 16

fig, ax = plt.subplots(figsize=(10.5, 6.4), dpi=140)

x = np.arange(len(sites))
width = 0.36


def floating_bars(ax, x_positions, ranges, color, label=None):
    lows = np.array([r[0] for r in ranges], dtype=float)
    highs = np.array([r[1] for r in ranges], dtype=float)
    heights = highs - lows
    return ax.bar(
        x_positions,
        heights,
        bottom=lows,
        width=width,
        color=color,
        edgecolor="#222222",
        linewidth=1.1,
        label=label,
        alpha=0.92,
    )


floating_bars(ax, x - width / 2, token_rev, TOKEN_COLOR, "AI factory (token sales)")
floating_bars(ax, x + width / 2, commodity_rev, COMMODITY_COLOR,
              "Main commodity product")

ax.set_yscale("log")
ax.set_ylim(5, 60000)
ax.set_ylabel("Annual revenue (USD millions, log scale)", fontsize=16)
ax.set_xticks(x)
ax.set_xticklabels(sites, fontsize=13.5, rotation=45, ha="right")
ax.tick_params(axis="y", labelsize=14)
ax.yaxis.grid(True, linestyle=":", color="#cccccc",
              linewidth=0.7, which="both")
ax.set_axisbelow(True)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Token (blue) labels go BELOW the blue boxes so they don't collide with the
# adjacent orange commodity bars. Commodity (orange) labels stay above.
for xp, (lo, hi) in zip(x - width / 2, token_rev):
    ax.text(xp, lo / 1.45, f"${lo}-{hi}M",
            ha="center", va="top", fontsize=14,
            color=TOKEN_COLOR, weight="bold")
for xp, (lo, hi) in zip(x + width / 2, commodity_rev):
    label = f"${lo/1000:.1f}-{hi/1000:.0f}B" if hi >= 1000 else f"${lo}-{hi}M"
    ax.text(xp, hi * 1.22, label,
            ha="center", va="bottom", fontsize=14,
            color=COMMODITY_COLOR, weight="bold")

# Title is rendered in the surrounding HTML (p.table-title), not on the image
# itself, so we don't bake it into the figure. Legend sits in the upper-right
# where the bars are short.
ax.legend(loc="upper right", fontsize=14, frameon=False)

# Explicit margins so the y-axis label has room; bbox_inches="tight" with a
# small pad then auto-expands the save bbox so the 45-deg x-tick labels at
# the left edge don't get clipped either.
plt.subplots_adjust(left=0.13, right=0.98, top=0.97, bottom=0.28)

out_path = "/sessions/loving-jolly-bell/mnt/EnergyFlux/blog/_sources/blog1_fig6_token_vs_commodity.png"
plt.savefig(out_path, dpi=140, bbox_inches="tight", pad_inches=0.15, facecolor="white")
print(f"Wrote {out_path}")

import os
size = os.path.getsize(out_path)
print(f"File size: {size/1024:.0f} KB")
