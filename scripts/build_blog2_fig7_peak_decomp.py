"""
Blog 2 Figure 7 — Peak grid demand decomposition vs transformer headroom.

Shows for each archetype (30/40/50/60 MGD) the worst-case peak grid demand
broken into its three contributors (AI rack facility load + BESS charging +
WWTP baseline) and overlays the typical service-transformer capacity at two
sizing conventions (1.07x lean, 1.4x typical real-world). Visualizes which
archetypes need a transformer upgrade and which fit inside the existing
service.

Output: blog/_sources/blog2_fig7_peak_decomp.png
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
keys = ["wwtp_30mgd", "wwtp_40mgd", "wwtp_50mgd", "wwtp_60mgd"]
labels = ["30 MGD", "40 MGD", "50 MGD", "60 MGD"]

wwtp_kw = [results[k]["site"]["wwtp_load_kw"] for k in keys]
ai_kw = [results[k]["dc"]["facility_load_mw"] * 1000.0 for k in keys]
bess_charge_kw = [results[k]["bess"]["max_charge_kw"] for k in keys]

# Total stack: WWTP baseline + AI facility + BESS charge
stack_total = [w + a + b for w, a, b in zip(wwtp_kw, ai_kw, bess_charge_kw)]

# Transformer capacity at two common sizings
xfmr_lean = [w * 1.07 for w in wwtp_kw]   # tight, 4 MVA for 45 MGD case
xfmr_typical = [w * 1.4 for w in wwtp_kw]  # typical real-world


# ---- Plot ----
fig, ax = plt.subplots(figsize=(11, 6.5))

BLUE = "#1F4E79"
GOLD = "#E8A33D"
GREEN = "#548235"
PURPLE = "#76448A"
GREY = "#7F7F7F"
RED = "#C00000"

x = np.arange(len(labels))
w = 0.55

# Stacked bars
b1 = ax.bar(x, wwtp_kw, w, color=GREY, label="WWTP baseline (already on feeder)", alpha=0.75)
b2 = ax.bar(x, ai_kw, w, bottom=wwtp_kw, color=PURPLE, label="AI rack facility load (with PUE)", alpha=0.85)
b3 = ax.bar(x, bess_charge_kw, w,
            bottom=[w_ + a_ for w_, a_ in zip(wwtp_kw, ai_kw)],
            color=GREEN, label="BESS max charging power", alpha=0.85)

# Transformer capacity overlays
ax.plot(x, xfmr_lean, "--", color=RED, linewidth=2, marker="o",
        label="Lean transformer (1.07× WWTP peak)")
ax.plot(x, xfmr_typical, "--", color=BLUE, linewidth=2, marker="s",
        label="Typical real-world transformer (1.4× WWTP peak)")

# Annotate stack totals
for i, total in enumerate(stack_total):
    ax.text(i, total + 200, f"{total:.0f} kW", ha="center", fontsize=9, fontweight="bold")

# Style
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=11)
ax.set_ylabel("Peak grid demand at worst-case simultaneity (kW)", fontsize=11)
ax.set_title("Peak grid demand decomposition — conservative (worst-case simultaneity) sizing\n"
             "vs. typical service-transformer capacity at two sizing conventions",
             fontsize=12, fontweight="bold", color=BLUE, pad=15)
ax.legend(loc="upper left", fontsize=9.5, frameon=True, framealpha=0.95)
ax.grid(axis="y", linestyle="--", alpha=0.3)
ax.set_axisbelow(True)
ax.set_ylim(0, max(stack_total) * 1.18)

# Add annotation explaining the gap
ax.annotate(
    "Stack above the dashed line = transformer\nupgrade required under static sizing",
    xy=(3, max(xfmr_typical) * 1.07),
    xytext=(2.5, max(stack_total) * 1.05),
    fontsize=9, ha="center", style="italic", color=RED,
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor=RED, alpha=0.9),
)


# ---- Save ----
out = os.path.join(os.path.dirname(__file__), "..", "blog", "_sources",
                   "blog2_fig7_peak_decomp.png")
fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
print(f"Saved {out}")
print(f"Image size: {os.path.getsize(out)} bytes")
print()
print("Stack values (kW):")
for label, w_, a_, b_, t in zip(labels, wwtp_kw, ai_kw, bess_charge_kw, stack_total):
    print(f"  {label}: WWTP {w_:.0f} + AI {a_:.0f} + BESS_charge {b_:.0f} = {t:.0f}")
print(f"\nXfmr lean (1.07x):    {[f'{x:.0f}' for x in xfmr_lean]}")
print(f"Xfmr typical (1.4x):  {[f'{x:.0f}' for x in xfmr_typical]}")
