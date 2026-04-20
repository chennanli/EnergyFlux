"""Block definitions for the Blog 2 flowsheet UI.

Each block is a typed dictionary with position, size, color, params, and
computed outputs. Blocks are addressed by a short stable ID (``"pv"``,
``"inv"``, ``"bess"``, ``"dc"``, ``"wwtp"``, ``"grid"``). The full design
state is ``dict[str, Block]`` and lives in ``st.session_state.design``.

Design philosophy
-----------------
1. **Blocks own their inputs (params), not their outputs.** Outputs are
   recomputed from params + upstream block outputs by ``recompute_all()``.
   This avoids stale state.

2. **Power flows forward only.** No feedback loops in MVP.
   ``RECOMPUTE_ORDER`` is a hand-specified topological order.

3. **All numeric quantities are SI.** Powers in kW, energies in MWh or
   kWh (noted), money in USD/year, land in acres (US convention).

4. **Engineer-editable params are at the top of each ``_default_*``
   function;** computed fields come from ``compute_*``. A reader wanting
   to learn the model reads the two functions in order.

Interaction with existing modules
---------------------------------
* ``stage1_5_wwtp_dc.design.pv_tools`` → drives the PV + inverter blocks.
* ``stage1_5_wwtp_dc.design.archetypes`` → defaults for hardware catalog + BESS.
* ``stage1_5_wwtp_dc.design.sizing`` → revenue calc at 4 token-price points.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

from stage1_5_wwtp_dc.design.pv_tools import (
    array_layout,
    calc_annual_yield,
    design_pv_array,
)
from stage1_5_wwtp_dc.design.archetypes import PRICE_POINTS_USD_PER_MTOKEN


# ---------------------------------------------------------------------------
# Visual constants — palette matches Blog 1 blue (#1F4E79)
# ---------------------------------------------------------------------------
BLOCK_COLORS: Dict[str, str] = {
    "pv":   "#E8A33D",   # solar amber
    "inv":  "#4A78A8",   # inverter blue
    "bess": "#4CAF50",   # battery green
    "dc":   "#1F4E79",   # DC deep blue (Blog 1 primary)
    "rack": "#76448A",   # AI rack purple — distinct from DC bus
    "wwtp": "#8a6d5f",   # plant brown
    "grid": "#9AA6B2",   # grid gray
}
BLOCK_TEXT_ON = "#FFFFFF"
BLOCK_SELECTED_BORDER = "#FFD166"
BLOCK_NORMAL_BORDER = "#FFFFFF"


# ---------------------------------------------------------------------------
# Block layout on the flowsheet canvas (coordinates in abstract units)
# ---------------------------------------------------------------------------
# The canvas is 12 × 10. Top-left origin, y grows downward.
# Blocks are laid out left-to-right along power-flow direction:
#   WWTP (top-left)
#   PV ──▶ Inverter ──▶ DC Bus ──▶ AI Rack (DC)
#                          │
#                          └──▶ BESS
#                          Grid (at top, feeds DC Bus)
BLOCK_LAYOUT: Dict[str, Dict[str, float]] = {
    # id     x    y    w    h
    "grid": {"x": 0.5, "y": 0.4, "w": 1.6, "h": 1.2},
    "wwtp": {"x": 0.5, "y": 4.3, "w": 1.6, "h": 1.4},
    "pv":   {"x": 0.5, "y": 7.2, "w": 1.6, "h": 1.6},
    "inv":  {"x": 4.0, "y": 7.2, "w": 1.6, "h": 1.6},
    "bess": {"x": 4.0, "y": 4.3, "w": 1.6, "h": 1.4},
    "dc":   {"x": 7.5, "y": 4.3, "w": 1.9, "h": 4.5},  # tall: aggregator
    "rack": {"x": 10.5, "y": 4.3, "w": 1.3, "h": 4.5},
}

# Connection edges: (from, to, label_position_fraction, label_prefix)
# Each edge is rendered as an arrow with a live power-flow label.
FLOWSHEET_EDGES: List[Tuple[str, str, str]] = [
    ("pv",   "inv",  "kW DC"),
    ("inv",  "dc",   "kW AC"),
    ("grid", "dc",   "kW import"),
    ("wwtp", "dc",   "kW load"),
    ("dc",   "bess", "kW charge/disch"),
    ("dc",   "rack", "kW IT"),
]

# Order in which blocks recompute. Upstream before downstream.
# Dependencies:
#   pv     — reads only its own params (+ inv.params.ilr/kw_each)
#   inv    — reads pv.outputs
#   wwtp   — self-contained
#   rack   — reads pv.outputs (kwp_dc) + dc.params.it_load_share
#   bess   — reads rack.outputs (it_mw)        ← must follow rack
#   dc     — reads pv, inv, wwtp, rack, bess   ← must follow all of them
#   grid   — reads dc.outputs
RECOMPUTE_ORDER: List[str] = ["pv", "inv", "wwtp", "rack", "bess", "dc", "grid"]


# ---------------------------------------------------------------------------
# Hardware catalog for AI-rack block
# ---------------------------------------------------------------------------
HARDWARE_CATALOG: Dict[str, Dict[str, Any]] = {
    "blackwell_gb200": {
        "label": "NVIDIA Blackwell GB200 NVL72",
        "rack_kw": 125.0,
        "tokens_per_sec_per_mw": 5.8e6,
        "pue": 1.25,
        "wiki": "hardware/blackwell_gb200_nvl72.md",
        "caveat": "Shipping in volume since Q3 2025.",
    },
    "vera_rubin": {
        "label": "NVIDIA Vera Rubin NVL144 (2026 estimate, ±30%)",
        "rack_kw": 175.0,
        "tokens_per_sec_per_mw": 1.1e7,
        "pue": 1.20,
        "wiki": "hardware/vera_rubin_nvl144.md",
        "caveat": "2026 H2 ship, estimates ±30% until field data exists.",
    },
    "amd_mi300x": {
        "label": "AMD Instinct MI300X (HGX 8-GPU chassis)",
        "rack_kw": 70.0,
        "tokens_per_sec_per_mw": 4.8e6,
        "pue": 1.25,
        "wiki": "hardware/amd_mi300x.md",
        "caveat": "Lower density, often better $/token at 2025 prices.",
    },
    "cerebras_wse3": {
        "label": "Cerebras WSE-3 (CS-3 appliance)",
        "rack_kw": 46.0,
        "tokens_per_sec_per_mw": 6.5e6,
        "pue": 1.22,
        "wiki": "hardware/cerebras_wse3.md",
        "caveat": "Wafer-scale, niche latency-optimized workloads.",
    },
}


# ===========================================================================
#                          BLOCK FACTORIES
# ===========================================================================
def default_design() -> Dict[str, Dict[str, Any]]:
    """Build the starting design — reasonable defaults for an Austin 23-acre site."""
    return {
        "pv":   _default_pv(),
        "inv":  _default_inv(),
        "bess": _default_bess(),
        "dc":   _default_dc(),
        "rack": _default_rack(),
        "wwtp": _default_wwtp(),
        "grid": _default_grid(),
    }


def _default_pv() -> Dict[str, Any]:
    return {
        "id": "pv",
        "kind": "pv",
        "label": "PV Array",
        "params": {
            "area_acres": 23.0,
            "module_w": 580,
            "tracking": "single_axis",
            "bifacial": True,
            "gcr": 0.35,
            "modules_per_tracker": 90,
            "lat": 30.27,
            "performance_ratio": 0.82,
        },
        "outputs": {},
    }


def _default_inv() -> Dict[str, Any]:
    return {
        "id": "inv",
        "kind": "inv",
        "label": "Inverters",
        "params": {
            "kw_each": 550,
            "ilr": 1.25,
            "efficiency": 0.975,
            "topology": "string",
        },
        "outputs": {},
    }


def _default_bess() -> Dict[str, Any]:
    return {
        "id": "bess",
        "kind": "bess",
        "label": "BESS",
        "params": {
            "duration_hours": 4.0,
            "sizing_basis": "dc_it_load",  # "dc_it_load" or "manual_mwh"
            "manual_mwh": 8.0,
            "chg_disch_ratio": 0.5,
            "round_trip_eff": 0.92,
            "soc_min_pct": 0.10,
            "soc_max_pct": 0.95,
        },
        "outputs": {},
    }


def _default_dc() -> Dict[str, Any]:
    return {
        "id": "dc",
        "kind": "dc",
        "label": "DC Bus",
        "params": {
            "voltage_kv": 0.48,           # 480 V AC distribution
            "it_load_share_of_pv_kwp": 0.35,
            "sla_tier_mix": {
                "p50": 0.50,
                "p95": 0.35,
                "p99": 0.15,
            },
        },
        "outputs": {},
    }


def _default_rack() -> Dict[str, Any]:
    return {
        "id": "rack",
        "kind": "rack",
        "label": "AI Racks",
        "params": {
            "hardware_key": "blackwell_gb200",
            "utilization": 0.70,
        },
        "outputs": {},
    }


def _default_wwtp() -> Dict[str, Any]:
    return {
        "id": "wwtp",
        "kind": "wwtp",
        "label": "WWTP Load",
        "params": {
            "mgd": 45.0,
            "kw_per_mgd": 83.33,
            "biogas_offset_kw": 800.0,
        },
        "outputs": {},
    }


def _default_grid() -> Dict[str, Any]:
    return {
        "id": "grid",
        "kind": "grid",
        "label": "Utility Grid",
        "params": {
            "service_voltage_kv": 25.0,
            "existing_xfmr_mva": 4.0,
            "transformer_upgrade_cost_usd": 300_000,
        },
        "outputs": {},
    }


# ===========================================================================
#                          COMPUTE FUNCTIONS
# ===========================================================================
def recompute_all(design: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Walk blocks in RECOMPUTE_ORDER; each compute fn reads params + any
    already-computed upstream outputs and writes its own outputs in place.

    Returns the same design dict (mutated). Callers can keep the reference.
    """
    for block_id in RECOMPUTE_ORDER:
        fn = _COMPUTE_FNS[block_id]
        design[block_id]["outputs"] = fn(design)
    return design


def _compute_pv(design: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    p = design["pv"]["params"]
    d = design_pv_array(
        area_acres=p["area_acres"],
        module_w=p["module_w"],
        tracking=p["tracking"],
        bifacial=p["bifacial"],
        ilr=design["inv"]["params"]["ilr"],
        inverter_kw=design["inv"]["params"]["kw_each"],
    )
    y = calc_annual_yield(
        kwp_dc=d["kwp_dc"],
        lat=p["lat"],
        tracking=p["tracking"],
        bifacial=p["bifacial"],
        performance_ratio=p["performance_ratio"],
    )
    # Layout is a function of kwp / area; used by pv_layout_viz.py.
    layout = array_layout(d)
    return {
        "kwp_dc": d["kwp_dc"],
        "module_count": d["module_count"],
        "string_count": d["string_count"],
        "modules_per_string": d["modules_per_string"],
        "inverter_count_recommended": d["inverter_count"],
        "annual_mwh": y["annual_mwh"],
        "capacity_factor_pct": y["capacity_factor_pct"],
        "specific_yield": y["specific_yield_kwh_per_kwp"],
        "zone": y["zone"],
        "dimensions_m": d["dimensions_m"],
        "layout_rects": layout,
        "tracking_effective": d["tracking"],
        "notes": d["notes"],
    }


def _compute_inv(design: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Inverter count is recommended by the PV block but editable here."""
    pv_out = design["pv"]["outputs"]
    p = design["inv"]["params"]
    count = pv_out.get("inverter_count_recommended", 11)
    total_kw_ac = count * p["kw_each"]
    return {
        "count": count,
        "total_kw_ac": total_kw_ac,
        "effective_ilr": (pv_out.get("kwp_dc", 0.0) / total_kw_ac) if total_kw_ac > 0 else 0.0,
        "output_kw_ac": total_kw_ac * p["efficiency"],
    }


def _compute_wwtp(design: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    p = design["wwtp"]["params"]
    load = p["mgd"] * p["kw_per_mgd"]
    net_grid_draw = max(load - p["biogas_offset_kw"], 0.0)
    return {
        "load_kw": load,
        "net_grid_draw_kw": net_grid_draw,
        "biogas_offset_kw": p["biogas_offset_kw"],
    }


def _compute_rack(design: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Rack count + IT MW come from the DC bus IT load share."""
    p = design["rack"]["params"]
    hw = HARDWARE_CATALOG[p["hardware_key"]]
    # DC IT MW is decided by the DC bus block's it_load_share_of_pv_kwp; we
    # read the DC bus's target here, but DC bus itself runs later and uses
    # our output. So we compute IT MW from upstream PV only.
    pv_kwp = design["pv"]["outputs"].get("kwp_dc", 0.0)
    share = design["dc"]["params"]["it_load_share_of_pv_kwp"]
    it_mw = share * pv_kwp / 1000.0
    racks = max(1, round(it_mw * 1000.0 / hw["rack_kw"]))
    facility_mw = it_mw * hw["pue"]
    tokens_per_sec = it_mw * hw["tokens_per_sec_per_mw"]
    return {
        "hardware_label": hw["label"],
        "hardware_caveat": hw["caveat"],
        "hardware_wiki": hw["wiki"],
        "it_mw": round(it_mw, 3),
        "facility_mw": round(facility_mw, 3),
        "pue": hw["pue"],
        "racks": racks,
        "rack_kw": hw["rack_kw"],
        "tokens_per_sec": tokens_per_sec,
        "utilization": p["utilization"],
    }


def _compute_bess(design: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    p = design["bess"]["params"]
    it_mw = design["rack"]["outputs"].get("it_mw", 2.0)
    if p["sizing_basis"] == "dc_it_load":
        mwh = it_mw * p["duration_hours"]
    else:
        mwh = p["manual_mwh"]
    max_disch_kw = it_mw * 1000.0
    max_chg_kw = max_disch_kw * p["chg_disch_ratio"]
    return {
        "mwh": round(mwh, 2),
        "duration_hours": p["duration_hours"],
        "max_charge_kw": round(max_chg_kw, 1),
        "max_discharge_kw": round(max_disch_kw, 1),
        "round_trip_eff": p["round_trip_eff"],
        "soc_min_kwh": mwh * 1000.0 * p["soc_min_pct"],
        "soc_max_kwh": mwh * 1000.0 * p["soc_max_pct"],
    }


def _compute_dc(design: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """DC Bus is the aggregator. Totals flows in/out + peak grid import."""
    pv = design["pv"]["outputs"]
    inv = design["inv"]["outputs"]
    wwtp = design["wwtp"]["outputs"]
    rack = design["rack"]["outputs"]
    bess = design["bess"]["outputs"]

    # Peak added load on utility transformer = facility DC + BESS charge.
    # WWTP baseline was already on the feeder pre-project; not added.
    peak_added_kw = rack["facility_mw"] * 1000.0 + bess["max_charge_kw"]

    # Revenue at 4 price points (same formula as design.sizing).
    import math
    sec_per_year = 365 * 24 * 3600
    realized_tokens = rack["tokens_per_sec"] * sec_per_year * rack["utilization"]
    realized_mtokens = realized_tokens / 1e6
    revenue = {
        f"{p:.2f}": round(realized_mtokens * p, 0)
        for p in PRICE_POINTS_USD_PER_MTOKEN
    }

    return {
        "voltage_kv": design["dc"]["params"]["voltage_kv"],
        "inflow_pv_ac_kw": inv["output_kw_ac"],
        "outflow_wwtp_kw": wwtp["net_grid_draw_kw"],
        "outflow_rack_kw": rack["facility_mw"] * 1000.0,
        "peak_added_to_grid_kw": peak_added_kw,
        "revenue_per_year_usd": revenue,
        "realized_tokens_per_year": realized_tokens,
    }


def _compute_grid(design: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    p = design["grid"]["params"]
    dc = design["dc"]["outputs"]
    peak_kw = dc.get("peak_added_to_grid_kw", 0.0)
    existing_kw = p["existing_xfmr_mva"] * 1000.0
    headroom = existing_kw - peak_kw
    upgrade_required = headroom < 500.0  # 500 kW safety margin
    return {
        "peak_added_kw": peak_kw,
        "existing_xfmr_kw": existing_kw,
        "headroom_kw": headroom,
        "upgrade_required": upgrade_required,
        "upgrade_cost_usd": p["transformer_upgrade_cost_usd"] if upgrade_required else 0,
    }


_COMPUTE_FNS = {
    "pv":   _compute_pv,
    "inv":  _compute_inv,
    "bess": _compute_bess,
    "dc":   _compute_dc,
    "rack": _compute_rack,
    "wwtp": _compute_wwtp,
    "grid": _compute_grid,
}


# ===========================================================================
#                          HEADLINE METRICS (for block labels)
# ===========================================================================
def headline_metric(block: Dict[str, Any]) -> str:
    """Short label shown inside the block on the flowsheet. Keeps labels
    tight; full detail is in the right-panel editor."""
    o = block.get("outputs", {})
    k = block["kind"]
    if k == "pv":
        kwp = o.get("kwp_dc", 0.0)
        return f"{kwp:,.0f} kWp DC"
    if k == "inv":
        c = o.get("count", 0)
        kw = block["params"]["kw_each"]
        return f"{c} × {kw} kW"
    if k == "bess":
        mwh = o.get("mwh", 0.0)
        h = o.get("duration_hours", 0.0)
        return f"{mwh:.1f} MWh ({h:.0f} h)"
    if k == "dc":
        v = block["params"]["voltage_kv"]
        kw = o.get("outflow_rack_kw", 0.0) + o.get("outflow_wwtp_kw", 0.0)
        return f"{v*1000:.0f} V  ·  {kw/1000:.1f} MW total"
    if k == "rack":
        it = o.get("it_mw", 0.0)
        r = o.get("racks", 0)
        return f"{it:.2f} MW IT  ·  {r} racks"
    if k == "wwtp":
        mgd = block["params"]["mgd"]
        kw = o.get("load_kw", 0.0)
        return f"{mgd:.0f} MGD  ·  {kw:,.0f} kW"
    if k == "grid":
        head = o.get("headroom_kw", 0.0)
        return f"{head:+,.0f} kW headroom"
    return ""


def edge_flow_kw(design: Dict[str, Dict[str, Any]], src: str, dst: str) -> float:
    """Compute the power flow (kW) that should be labeled on the edge src→dst."""
    if src == "pv" and dst == "inv":
        return design["pv"]["outputs"].get("kwp_dc", 0.0)
    if src == "inv" and dst == "dc":
        return design["inv"]["outputs"].get("output_kw_ac", 0.0)
    if src == "grid" and dst == "dc":
        return max(design["dc"]["outputs"].get("peak_added_to_grid_kw", 0.0), 0.0)
    if src == "wwtp" and dst == "dc":
        return design["wwtp"]["outputs"].get("net_grid_draw_kw", 0.0)
    if src == "dc" and dst == "bess":
        return design["bess"]["outputs"].get("max_charge_kw", 0.0)
    if src == "dc" and dst == "rack":
        return design["rack"]["outputs"].get("facility_mw", 0.0) * 1000.0
    return 0.0
