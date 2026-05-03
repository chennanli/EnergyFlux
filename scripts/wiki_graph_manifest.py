"""
Knowledge-graph manifest for the EnergyFlux design wiki and flowsheet blocks.

This is a hand-curated declaration of:
  - Engineering BLOCKS that appear on the flowsheet (PV, Inverter, BESS, ...)
  - WIKI entries that ground the copilot's answers (15 markdown files in
    stage1_5_wwtp_dc/design_wiki/)
  - EDGES that express two kinds of relationship:
      * power-flow / dependency edges between engineering blocks
        (matching the actual data flow in apps/flowsheet/blocks.py and
        the `peak_added_kW` math in design/sizing.py)
      * "informs" edges from wiki entries to the engineering blocks
        whose sizing assumptions they ground

The graph is rendered by build_blog2_fig8_wiki_graph.py into:
  - blog/_sources/blog2_fig8_wiki_graph.png   (matplotlib + networkx, blog-embeddable)
  - wiki_graph_interactive.html                (pyvis, interactive — for Streamlit tab)

This file is the single source of truth for the graph. Editing it changes
both renderings.

Curation principle: only encode relationships that are directly traceable to
either a real power-flow path in the running tool, or a wiki entry that
genuinely grounds a sizing assumption. No speculative or auto-inferred edges.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple


# ──────────────────────────────────────────────────────────────────────────
# Block / wiki node declarations
# ──────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Node:
    """One node on the knowledge graph."""
    id: str
    label: str
    category: str         # one of: pv, inverter, bess, dc, rack, wwtp, grid,
                          #   wiki-pv, wiki-bess, wiki-hardware, wiki-regulations, wiki-capex
    detail: str = ""      # subtitle / hover detail
    wiki_path: str = ""   # if a wiki node, relative path to the markdown file


# Top layer: engineering blocks (the flowsheet itself)
ENGINEERING_BLOCKS: List[Node] = [
    Node(id="pv",      label="PV Array",         category="pv",       detail="7,474 kWp single-axis bifacial"),
    Node(id="inv",     label="Inverter",         category="inverter", detail="11 × 550 kW central, ILR 1.25"),
    Node(id="bess",    label="BESS",             category="bess",     detail="10.5 MWh, 4-hour"),
    Node(id="dc",      label="DC Bus",           category="dc",       detail="480 V common bus"),
    Node(id="rack",    label="AI Racks",         category="rack",     detail="21 × NVL72 · 2.62 MW IT"),
    Node(id="wwtp",    label="WWTP Load",        category="wwtp",     detail="45 MGD · 3,750 kW peak"),
    Node(id="grid",    label="Service Xfmr",     category="grid",     detail="4 MVA · headroom check"),
]

# Bottom layer: wiki entries (15 markdown files, by category)
WIKI_PV: List[Node] = [
    Node(id="w_pv_single_axis",  label="single-axis tracker",   category="wiki-pv",
         detail="GCR + tracking", wiki_path="pv/single_axis_tracker.md"),
    Node(id="w_pv_bifacial",     label="bifacial gain",         category="wiki-pv",
         detail="albedo, pitch, height", wiki_path="pv/bifacial_gain.md"),
    Node(id="w_pv_fixed",        label="fixed tilt",            category="wiki-pv",
         detail="cheap baseline", wiki_path="pv/fixed_tilt.md"),
    Node(id="w_pv_dual",         label="dual-axis",             category="wiki-pv",
         detail="diminishing returns", wiki_path="pv/dual_axis.md"),
]

WIKI_BESS: List[Node] = [
    Node(id="w_bess_4hr",        label="4-hour BESS default",   category="wiki-bess",
         detail="industry default", wiki_path="bess/4h_battery_standard.md"),
    Node(id="w_bess_tou",        label="TOU arbitrage",         category="wiki-bess",
         detail="evening peak window", wiki_path="bess/tou_arbitrage.md"),
]

WIKI_HARDWARE: List[Node] = [
    Node(id="w_hw_blackwell",    label="Blackwell GB200 NVL72", category="wiki-hardware",
         detail="120 kW/rack liquid", wiki_path="hardware/blackwell_gb200_nvl72.md"),
    Node(id="w_hw_rubin",        label="Vera Rubin NVL144",     category="wiki-hardware",
         detail="170-200 kW/rack", wiki_path="hardware/vera_rubin_nvl144.md"),
    Node(id="w_hw_amd",          label="AMD MI300X",            category="wiki-hardware",
         detail="alt-vendor option", wiki_path="hardware/amd_mi300x.md"),
    Node(id="w_hw_cerebras",     label="Cerebras WSE-3",        category="wiki-hardware",
         detail="wafer-scale alt", wiki_path="hardware/cerebras_wse3.md"),
]

WIKI_REGULATIONS: List[Node] = [
    Node(id="w_reg_ercot",       label="ERCOT BTM rules",       category="wiki-regulations",
         detail="Texas BTM regs", wiki_path="regulations/tx_ercot_interconnect.md"),
    Node(id="w_reg_buffer",      label="WWTP buffer setbacks",  category="wiki-regulations",
         detail="setback codes", wiki_path="regulations/wwtp_buffer_setback.md"),
]

WIKI_CAPEX: List[Node] = [
    Node(id="w_cap_lazard_pv",   label="Lazard LCOE+ 2024",     category="wiki-capex",
         detail="$/MWh PV", wiki_path="capex/pv_lazard_lcoe_2024.md"),
    Node(id="w_cap_nrel_bess",   label="NREL ATB BESS 2024",    category="wiki-capex",
         detail="$/kWh storage", wiki_path="capex/bess_nrel_atb_2024.md"),
    Node(id="w_cap_dc",          label="DC industry benchmarks", category="wiki-capex",
         detail="$/kW facility", wiki_path="capex/dc_industry_benchmarks.md"),
]

ALL_WIKI_NODES = WIKI_PV + WIKI_BESS + WIKI_HARDWARE + WIKI_REGULATIONS + WIKI_CAPEX

ALL_NODES: List[Node] = ENGINEERING_BLOCKS + ALL_WIKI_NODES


# ──────────────────────────────────────────────────────────────────────────
# Edge declarations
# ──────────────────────────────────────────────────────────────────────────

# Power-flow edges: how blocks depend on each other in the running tool.
# Source of truth: apps/flowsheet/blocks.py RECOMPUTE_ORDER, and the
# `peak_added_kW = AI_facility_kW + BESS_max_charge_kW` formula in
# design/sizing.py. The graph reflects the actual two-path structure:
#   PV → Inverter → DC bus → AI racks (the new infrastructure path)
#   BESS ↔ DC bus (storage charges and discharges through the DC bus)
#   AI racks → Service transformer (new demand)
#   WWTP load → Service transformer (existing demand)
# The transformer is the constraint where headroom is checked.
POWER_FLOW_EDGES: List[Tuple[str, str, str]] = [
    ("pv",   "inv",  "DC power"),
    ("inv",  "dc",   "AC→DC bus"),
    ("bess", "dc",   "charge/discharge"),
    ("dc",   "rack", "DC supply to racks"),
    ("rack", "grid", "new demand at peak"),
    ("bess", "grid", "BESS charging draws from grid"),
    ("wwtp", "grid", "existing demand"),
]

# "Informs" edges: which wiki entries ground which sizing assumptions.
# Curated to mirror what design/sizing.py actually consults — no speculation.
INFORMS_EDGES: List[Tuple[str, str]] = [
    # PV-side wiki → PV block
    ("w_pv_single_axis",  "pv"),
    ("w_pv_bifacial",     "pv"),
    ("w_pv_fixed",        "pv"),
    ("w_pv_dual",         "pv"),
    # PV CAPEX → PV block
    ("w_cap_lazard_pv",   "pv"),
    # BESS wiki → BESS block
    ("w_bess_4hr",        "bess"),
    ("w_bess_tou",        "bess"),
    ("w_cap_nrel_bess",   "bess"),
    # Hardware wiki → AI racks
    ("w_hw_blackwell",    "rack"),
    ("w_hw_rubin",        "rack"),
    ("w_hw_amd",          "rack"),
    ("w_hw_cerebras",     "rack"),
    # DC industry CAPEX → AI rack facility cost
    ("w_cap_dc",          "rack"),
    # Regulations
    ("w_reg_ercot",       "grid"),    # interconnection rules
    ("w_reg_buffer",      "wwtp"),    # buffer/setback rules anchor on WWTP siting
]


# ──────────────────────────────────────────────────────────────────────────
# Style hints (consumed by the renderer)
# ──────────────────────────────────────────────────────────────────────────

CATEGORY_COLORS = {
    "pv":               "#E8A33D",   # gold, matches blog hero
    "inverter":         "#9DC3E6",   # light blue
    "bess":             "#548235",   # green
    "dc":               "#1F4E79",   # blog primary blue
    "rack":             "#76448A",   # purple
    "wwtp":             "#7F7F7F",   # grey
    "grid":             "#C00000",   # red — the constraint
    # wiki categories — softer pastels of the blocks they inform
    "wiki-pv":           "#F4D8A8",
    "wiki-bess":         "#C6DEB1",
    "wiki-hardware":     "#D7BFE0",
    "wiki-regulations":  "#F4B7B7",
    "wiki-capex":        "#D9D9D9",
}

CATEGORY_LABELS = {
    "pv":               "PV array",
    "inverter":         "Inverter",
    "bess":             "BESS",
    "dc":               "DC bus",
    "rack":             "AI racks",
    "wwtp":             "WWTP load",
    "grid":             "Service transformer",
    "wiki-pv":           "Wiki — PV",
    "wiki-bess":         "Wiki — BESS",
    "wiki-hardware":     "Wiki — hardware",
    "wiki-regulations":  "Wiki — regulations",
    "wiki-capex":        "Wiki — CAPEX",
}

NODE_LOOKUP = {n.id: n for n in ALL_NODES}


def lint() -> List[str]:
    """Return a list of inconsistencies in the manifest. Empty list = clean."""
    issues = []

    # All edge endpoints must exist in NODE_LOOKUP.
    for src, dst, _ in POWER_FLOW_EDGES:
        for nid in (src, dst):
            if nid not in NODE_LOOKUP:
                issues.append(f"power-flow edge endpoint {nid!r} not in NODE_LOOKUP")

    for src, dst in INFORMS_EDGES:
        for nid in (src, dst):
            if nid not in NODE_LOOKUP:
                issues.append(f"informs edge endpoint {nid!r} not in NODE_LOOKUP")

    # Wiki paths should be valid filenames (basic format check).
    for n in ALL_WIKI_NODES:
        if not n.wiki_path.endswith(".md"):
            issues.append(f"wiki node {n.id!r} has non-.md path {n.wiki_path!r}")

    # Categories must be in CATEGORY_COLORS.
    for n in ALL_NODES:
        if n.category not in CATEGORY_COLORS:
            issues.append(f"node {n.id!r} has unknown category {n.category!r}")

    return issues


if __name__ == "__main__":
    # Self-check on import
    issues = lint()
    if issues:
        print("Manifest lint FAILED:")
        for i in issues:
            print(f"  - {i}")
        raise SystemExit(1)
    print(f"Manifest OK: {len(ENGINEERING_BLOCKS)} blocks, {len(ALL_WIKI_NODES)} wiki entries, "
          f"{len(POWER_FLOW_EDGES)} power-flow edges, {len(INFORMS_EDGES)} informs edges.")
