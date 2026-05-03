"""
Blog 2 Figure 8 — hand-curated knowledge graph of the EnergyFlux design wiki
plus the engineering blocks it grounds.

Reads the manifest in scripts/wiki_graph_manifest.py and renders a static PNG
for blog embedding. Layout is hand-positioned for a two-band visual:
  - Top band: engineering blocks in a flow-chart layout that matches the
    actual power-flow / dependency structure of the running tool.
  - Bottom band: wiki entries clustered by category, each with a soft
    "informs" line to the engineering block(s) it grounds.

Output: blog/_sources/blog2_fig8_wiki_graph.png

Why no networkx, no pyvis:
  - Both are absent from this sandbox and we want the figure today.
  - For a 22-node curated graph the visual narrative is best served by
    explicit positions, not by a force-directed layout that produces
    overlapping labels.
  - The manifest in wiki_graph_manifest.py is the single source of truth;
    layout decisions live in this file alone.
"""
import os
import sys

# Make the manifest importable when running from repo root.
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D

from wiki_graph_manifest import (
    NODE_LOOKUP,
    POWER_FLOW_EDGES,
    INFORMS_EDGES,
    CATEGORY_COLORS,
    CATEGORY_LABELS,
    ENGINEERING_BLOCKS,
    WIKI_PV,
    WIKI_BESS,
    WIKI_HARDWARE,
    WIKI_REGULATIONS,
    WIKI_CAPEX,
    lint,
)


# ──────────────────────────────────────────────────────────────────────────
# Step 0: lint manifest before doing anything
# ──────────────────────────────────────────────────────────────────────────
issues = lint()
if issues:
    print("Manifest lint FAILED — refusing to render. Issues:")
    for i in issues:
        print(f"  - {i}")
    raise SystemExit(1)


# ──────────────────────────────────────────────────────────────────────────
# Step 1: hand-positioned coordinates
# ──────────────────────────────────────────────────────────────────────────
# Coordinates are in figure-internal units. The figure is 16 wide × 11 tall.
# Top band y ≈ 7.5–9.0 (engineering blocks).
# Bottom band y ≈ 0.5–4.5 (wiki entries, clustered by category).

TOP_Y = 8.4
BOTTOM_Y_PV       = 4.3
BOTTOM_Y_BESS     = 4.3
BOTTOM_Y_HW       = 4.3
BOTTOM_Y_REG      = 4.3
BOTTOM_Y_CAPEX    = 2.4

POSITIONS = {
    # ── Top band: engineering blocks ───────────────────────────────
    # Flow: PV → Inverter → DC bus → AI Racks → Service Transformer
    #              ↑                              ↑
    #            BESS                         WWTP load
    "pv":       (1.7,  TOP_Y),
    "inv":      (4.4,  TOP_Y),
    "dc":       (7.1,  TOP_Y),
    "rack":     (9.8,  TOP_Y),
    "grid":     (13.0, TOP_Y),
    "bess":     (7.1,  TOP_Y - 1.7),    # below DC bus
    "wwtp":     (13.0, TOP_Y - 1.7),    # below grid (its existing demand)

    # ── Bottom band: wiki entries ──────────────────────────────────
    # PV wiki cluster (under PV block)
    "w_pv_single_axis":  (0.6,  BOTTOM_Y_PV),
    "w_pv_bifacial":     (2.0,  BOTTOM_Y_PV),
    "w_pv_fixed":        (0.6,  BOTTOM_Y_PV - 0.95),
    "w_pv_dual":         (2.0,  BOTTOM_Y_PV - 0.95),

    # BESS wiki cluster (under BESS block)
    "w_bess_4hr":        (6.1,  BOTTOM_Y_BESS),
    "w_bess_tou":        (7.7,  BOTTOM_Y_BESS),

    # Hardware wiki cluster (under AI Racks)
    "w_hw_blackwell":    (8.9,  BOTTOM_Y_HW),
    "w_hw_rubin":        (10.4, BOTTOM_Y_HW),
    "w_hw_amd":          (8.9,  BOTTOM_Y_HW - 0.95),
    "w_hw_cerebras":     (10.4, BOTTOM_Y_HW - 0.95),

    # Regulations cluster (right side, well clear of hardware)
    "w_reg_ercot":       (13.4, BOTTOM_Y_REG),
    "w_reg_buffer":      (13.4, BOTTOM_Y_REG - 0.95),

    # CAPEX cluster — lower row, sweeping under the whole top band
    "w_cap_lazard_pv":   (3.0,  BOTTOM_Y_CAPEX),
    "w_cap_nrel_bess":   (7.0,  BOTTOM_Y_CAPEX),
    "w_cap_dc":          (10.5, BOTTOM_Y_CAPEX),
}

# Sanity check: every node has a position
missing = [n for n in NODE_LOOKUP if n not in POSITIONS]
if missing:
    raise RuntimeError(f"missing positions for nodes: {missing}")


# ──────────────────────────────────────────────────────────────────────────
# Step 2: figure setup
# ──────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(18, 11.5))
ax.set_xlim(-0.7, 15.4)
ax.set_ylim(-1.0, 10.5)
ax.axis("off")
fig.patch.set_facecolor("white")

# Light visual band markers to separate top (blocks) and bottom (wiki).
ax.axhline(y=6.5, color="#BFBFBF", linestyle=":", linewidth=0.8, alpha=0.6)
ax.text(-0.4, 9.5, "Engineering blocks (the flowsheet)",
        fontsize=11.5, fontweight="bold", color="#1F4E79")
ax.text(-0.4, 5.3, "Wiki entries (the cited source material the copilot retrieves from)",
        fontsize=11.5, fontweight="bold", color="#1F4E79")


# ──────────────────────────────────────────────────────────────────────────
# Step 3: draw "informs" edges first (so they sit behind the nodes)
# ──────────────────────────────────────────────────────────────────────────
INFORMS_EDGE_STYLE = dict(
    color="#9DC3E6", linestyle="-", linewidth=0.75, alpha=0.55, zorder=1,
)

for src_id, dst_id in INFORMS_EDGES:
    x0, y0 = POSITIONS[src_id]
    x1, y1 = POSITIONS[dst_id]
    ax.plot([x0, x1], [y0, y1], **INFORMS_EDGE_STYLE)


# ──────────────────────────────────────────────────────────────────────────
# Step 4: draw power-flow edges (arrows, on top of informs lines)
# ──────────────────────────────────────────────────────────────────────────
def draw_arrow(ax, src, dst, color, label=None):
    x0, y0 = POSITIONS[src]
    x1, y1 = POSITIONS[dst]
    arrow = FancyArrowPatch(
        (x0, y0), (x1, y1),
        arrowstyle="->,head_length=8,head_width=5",
        color=color,
        linewidth=2.2,
        connectionstyle="arc3,rad=0.0",
        shrinkA=22, shrinkB=22,
        zorder=3,
    )
    ax.add_patch(arrow)
    if label:
        ax.text((x0 + x1) / 2, (y0 + y1) / 2 + 0.18, label,
                fontsize=8.5, color=color, ha="center", style="italic", zorder=4)

POWER_FLOW_COLOR = "#1F4E79"
for src, dst, label in POWER_FLOW_EDGES:
    draw_arrow(ax, src, dst, POWER_FLOW_COLOR, label=label)


# ──────────────────────────────────────────────────────────────────────────
# Step 5: draw nodes (engineering blocks larger; wiki entries smaller)
# ──────────────────────────────────────────────────────────────────────────
def draw_block_node(ax, node, position, large=False):
    x, y = position
    color = CATEGORY_COLORS[node.category]
    if large:
        w, h = 2.05, 1.10
        fontsize_label = 11
        fontsize_detail = 8.5
        label_offset = 0.20
        detail_offset = -0.22
    else:
        w, h = 1.20, 0.70
        fontsize_label = 8.5
        fontsize_detail = 7
        label_offset = 0.13
        detail_offset = -0.16

    box = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.04,rounding_size=0.10",
        linewidth=1.0,
        edgecolor="#444",
        facecolor=color,
        zorder=5,
    )
    ax.add_patch(box)
    ax.text(x, y + label_offset, node.label,
            ha="center", va="center", fontsize=fontsize_label,
            fontweight="bold", color="#222", zorder=6)
    if node.detail:
        ax.text(x, y + detail_offset, node.detail,
                ha="center", va="center", fontsize=fontsize_detail,
                color="#222", zorder=6)


# Engineering blocks — large boxes
for n in ENGINEERING_BLOCKS:
    draw_block_node(ax, n, POSITIONS[n.id], large=True)

# Wiki entries — small boxes
for n in (WIKI_PV + WIKI_BESS + WIKI_HARDWARE + WIKI_REGULATIONS + WIKI_CAPEX):
    draw_block_node(ax, n, POSITIONS[n.id], large=False)


# ──────────────────────────────────────────────────────────────────────────
# Step 6: legend
# ──────────────────────────────────────────────────────────────────────────
legend_elements = [
    # Power-flow edge
    Line2D([0], [0], color=POWER_FLOW_COLOR, lw=2.5,
           label="Power-flow / dependency edge (matches sizing.py)"),
    # Informs edge
    Line2D([0], [0], color=INFORMS_EDGE_STYLE["color"], lw=1.5,
           linestyle="-", alpha=0.8,
           label="Wiki 'informs sizing assumption' edge"),
    # A node sample for each major category
    Line2D([0], [0], marker="s", color="w", markerfacecolor=CATEGORY_COLORS["pv"],
           markersize=12, label="PV-related"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor=CATEGORY_COLORS["bess"],
           markersize=12, label="BESS-related"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor=CATEGORY_COLORS["rack"],
           markersize=12, label="AI rack / hardware"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor=CATEGORY_COLORS["wwtp"],
           markersize=12, label="WWTP load"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor=CATEGORY_COLORS["grid"],
           markersize=12, label="Service transformer (constraint)"),
]
ax.legend(handles=legend_elements, loc="lower center", bbox_to_anchor=(0.5, -0.08),
          ncol=4, fontsize=9, framealpha=0.95, edgecolor="#BFBFBF")


# ──────────────────────────────────────────────────────────────────────────
# Step 7: title
# ──────────────────────────────────────────────────────────────────────────
fig.suptitle(
    "EnergyFlux Blog 2 — design wiki + flowsheet blocks, hand-curated",
    fontsize=13, fontweight="bold", color="#1F4E79", y=0.97,
)
fig.text(0.5, 0.93,
         "Top band: engineering blocks and the actual power-flow dependency from sizing.py.   "
         "Bottom band: 15 wiki entries grouped by category, each with a soft line to the block whose sizing assumptions it grounds.",
         ha="center", fontsize=9.5, style="italic", color="#444")


# ──────────────────────────────────────────────────────────────────────────
# Step 8: save
# ──────────────────────────────────────────────────────────────────────────
out = os.path.join(os.path.dirname(__file__), "..", "blog", "_sources",
                   "blog2_fig8_wiki_graph.png")
fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
print(f"Saved {out}")
print(f"Image size: {os.path.getsize(out)} bytes")
print(f"Nodes: {len(NODE_LOOKUP)} ({len(ENGINEERING_BLOCKS)} blocks + {len(NODE_LOOKUP) - len(ENGINEERING_BLOCKS)} wiki)")
print(f"Edges: {len(POWER_FLOW_EDGES)} power-flow + {len(INFORMS_EDGES)} informs")
