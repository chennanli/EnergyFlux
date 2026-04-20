"""Per-block parameter editors.

When a block is selected on the flowsheet canvas, the right-hand panel calls
the matching editor function. Each editor:

* Reads the block's current params from ``st.session_state.design``
* Renders sliders/selectboxes/inputs for every editable parameter
* Writes changes back to session_state
* Does NOT directly recompute — the caller does that after the editor returns
  so that all changes propagate in one consistent sweep

The editor functions return True if any parameter changed; the caller uses
that to decide whether to trigger a recompute this rerun.
"""
from __future__ import annotations

from typing import Any, Callable, Dict

import plotly.graph_objects as go
import streamlit as st

from stage1_5_wwtp_dc.design.pv_tools import MODULE_CATALOG
from stage1_5_wwtp_dc.design.archetypes import PRICE_POINTS_USD_PER_MTOKEN

from .blocks import HARDWARE_CATALOG
from .pv_layout_viz import build_tracker_farm_figure


def render_editor(
    block_id: str,
    design: Dict[str, Dict[str, Any]],
) -> bool:
    """Dispatch to the right editor; return True if any param changed."""
    fn = _DISPATCH.get(block_id)
    if fn is None:
        st.warning(f"No editor registered for block '{block_id}'.")
        return False
    return fn(design)


# ===========================================================================
#                               PV ARRAY
# ===========================================================================
def _editor_pv(design: Dict[str, Dict[str, Any]]) -> bool:
    block = design["pv"]
    p = block["params"]
    out = block.get("outputs", {})
    changed = False

    st.markdown("### ☀️ PV Array")
    st.caption(
        "Ground-mount single-axis tracker parameterization. "
        "Values feed `pvlib`-style sizing + annual-yield calc."
    )

    c1, c2 = st.columns(2)
    with c1:
        new_area = st.slider(
            "Buildable buffer area (acres)", 5.0, 60.0,
            float(p["area_acres"]), step=0.5, key="pv_area",
        )
        if new_area != p["area_acres"]:
            p["area_acres"] = new_area; changed = True

        new_lat = st.slider(
            "Site latitude (°N)", 24.0, 49.0,
            float(p["lat"]), step=0.1, key="pv_lat",
            help="Drives the specific-yield zone (south/central/north/far-north).",
        )
        if new_lat != p["lat"]:
            p["lat"] = new_lat; changed = True

        new_gcr = st.slider(
            "Ground coverage ratio (GCR)", 0.20, 0.50,
            float(p["gcr"]), step=0.01, key="pv_gcr",
            help="Lower GCR = wider row spacing, less shading, less density.",
        )
        if new_gcr != p["gcr"]:
            p["gcr"] = new_gcr; changed = True

    with c2:
        module_choices = sorted(MODULE_CATALOG.keys())
        new_mod = st.selectbox(
            "Module wattage",
            options=module_choices,
            index=module_choices.index(p["module_w"]),
            format_func=lambda w: f"{w} W — {MODULE_CATALOG[w]['technology']}",
            key="pv_module",
        )
        if new_mod != p["module_w"]:
            p["module_w"] = new_mod; changed = True

        tracking_opts = ["single_axis", "fixed_tilt", "dual_axis"]
        new_trk = st.selectbox(
            "Tracking",
            options=tracking_opts,
            index=tracking_opts.index(p["tracking"]) if p["tracking"] in tracking_opts else 0,
            key="pv_tracking",
        )
        if new_trk != p["tracking"]:
            p["tracking"] = new_trk; changed = True

        new_bif = st.checkbox(
            "Bifacial modules",
            value=bool(p["bifacial"]),
            key="pv_bifacial",
            help="Adds ~7% yield if combined with single-axis tracker (industry default).",
        )
        if new_bif != p["bifacial"]:
            p["bifacial"] = new_bif; changed = True

        new_mpt = st.slider(
            "Modules per tracker",
            30, 120, int(p["modules_per_tracker"]), step=2,
            key="pv_mpt",
            help="90 is industry typical for 1500 V strings.",
        )
        if new_mpt != p["modules_per_tracker"]:
            p["modules_per_tracker"] = new_mpt; changed = True

    # Key outputs panel
    st.markdown("---")
    st.markdown("**Computed outputs** (live, `pvlib`-equivalent):")
    cols = st.columns(4)
    cols[0].metric("DC nameplate", f"{out.get('kwp_dc', 0):,.0f} kWp")
    cols[1].metric("Modules", f"{out.get('module_count', 0):,}")
    cols[2].metric("Strings", f"{out.get('string_count', 0)}")
    cols[3].metric("Annual energy",
                   f"{out.get('annual_mwh', 0):,.0f} MWh",
                   f"CF {out.get('capacity_factor_pct', 0):.1f}%")

    # The star: tracker farm layout viz
    st.markdown("---")
    st.markdown("**Farm layout** — what's actually getting built on the parcel:")
    try:
        fig = build_tracker_farm_figure(block, fig_height=440)
        st.plotly_chart(fig, use_container_width=True, key="pv_layout_viz")
    except Exception as e:  # noqa: BLE001
        st.error(f"Layout viz failed: {e}")

    notes = out.get("notes", [])
    if notes:
        with st.expander("pvlib notes", expanded=False):
            for n in notes:
                st.markdown(f"- {n}")

    return changed


# ===========================================================================
#                               INVERTER
# ===========================================================================
def _editor_inv(design: Dict[str, Dict[str, Any]]) -> bool:
    block = design["inv"]
    p = block["params"]
    out = block.get("outputs", {})
    changed = False

    st.markdown("### 🔌 Inverters")
    st.caption("Central-inverter sizing. DC/AC ratio (ILR) 1.2-1.3 is industry norm.")

    c1, c2 = st.columns(2)
    with c1:
        kw_choices = [250, 350, 500, 550, 630, 800, 1000, 1250, 1500, 2000, 2500, 3125]
        new_kw = st.selectbox(
            "Per-inverter AC nameplate (kW)",
            options=kw_choices,
            index=kw_choices.index(p["kw_each"]) if p["kw_each"] in kw_choices else 3,
            key="inv_kw",
        )
        if new_kw != p["kw_each"]:
            p["kw_each"] = new_kw; changed = True

        new_ilr = st.slider(
            "DC/AC ratio (ILR)", 1.00, 1.50,
            float(p["ilr"]), step=0.01, key="inv_ilr",
            help="Higher ILR = more DC clipping but cheaper inverters.",
        )
        if new_ilr != p["ilr"]:
            p["ilr"] = new_ilr; changed = True

    with c2:
        new_eff = st.slider(
            "Peak efficiency",
            0.96, 0.995, float(p["efficiency"]), step=0.001, key="inv_eff",
            help="Modern central inverters run 97-98% at peak load.",
        )
        if new_eff != p["efficiency"]:
            p["efficiency"] = new_eff; changed = True

        new_topo = st.radio(
            "Topology",
            options=["string", "central"],
            horizontal=True,
            index=["string", "central"].index(p.get("topology", "string")),
            key="inv_topology",
        )
        if new_topo != p["topology"]:
            p["topology"] = new_topo; changed = True

    st.markdown("---")
    st.markdown("**Computed outputs:**")
    cols = st.columns(3)
    cols[0].metric("Count", f"{out.get('count', 0)}")
    cols[1].metric("Total AC nameplate", f"{out.get('total_kw_ac', 0):,.0f} kW")
    cols[2].metric("Effective ILR", f"{out.get('effective_ilr', 0):.2f}")

    return changed


# ===========================================================================
#                               BESS
# ===========================================================================
def _editor_bess(design: Dict[str, Dict[str, Any]]) -> bool:
    block = design["bess"]
    p = block["params"]
    out = block.get("outputs", {})
    changed = False

    st.markdown("### 🔋 Battery Energy Storage")
    st.caption(
        "Industry default: 4-hour Li-ion LFP. "
        "Duration tracks the on-peak window in TOU tariffs."
    )

    c1, c2 = st.columns(2)
    with c1:
        basis_opts = ["dc_it_load", "manual_mwh"]
        basis_labels = {"dc_it_load": "Auto-size to DC IT load",
                        "manual_mwh": "Manual MWh"}
        new_basis = st.radio(
            "Sizing basis",
            options=basis_opts,
            format_func=lambda x: basis_labels[x],
            index=basis_opts.index(p["sizing_basis"]),
            key="bess_basis",
            horizontal=False,
        )
        if new_basis != p["sizing_basis"]:
            p["sizing_basis"] = new_basis; changed = True

        if p["sizing_basis"] == "dc_it_load":
            new_dur = st.slider(
                "Duration (hours)", 1.0, 8.0,
                float(p["duration_hours"]), step=0.5, key="bess_dur",
            )
            if new_dur != p["duration_hours"]:
                p["duration_hours"] = new_dur; changed = True
        else:
            new_mwh = st.slider(
                "Manual MWh", 1.0, 40.0,
                float(p["manual_mwh"]), step=0.5, key="bess_mwh",
            )
            if new_mwh != p["manual_mwh"]:
                p["manual_mwh"] = new_mwh; changed = True

    with c2:
        new_ratio = st.slider(
            "Charge / discharge ratio",
            0.25, 1.0, float(p["chg_disch_ratio"]), step=0.05,
            key="bess_cdratio",
            help="0.5 = slow-charge, fast-discharge (stage 1 default).",
        )
        if new_ratio != p["chg_disch_ratio"]:
            p["chg_disch_ratio"] = new_ratio; changed = True

        new_rte = st.slider(
            "Round-trip efficiency",
            0.85, 0.95, float(p["round_trip_eff"]), step=0.005,
            key="bess_rte",
        )
        if new_rte != p["round_trip_eff"]:
            p["round_trip_eff"] = new_rte; changed = True

    st.markdown("---")
    st.markdown("**Computed outputs:**")
    cols = st.columns(3)
    cols[0].metric("Nameplate", f"{out.get('mwh', 0):.1f} MWh")
    cols[1].metric("Max discharge", f"{out.get('max_discharge_kw', 0):,.0f} kW")
    cols[2].metric("Max charge", f"{out.get('max_charge_kw', 0):,.0f} kW")

    return changed


# ===========================================================================
#                               AI RACKS
# ===========================================================================
def _editor_rack(design: Dict[str, Dict[str, Any]]) -> bool:
    block = design["rack"]
    p = block["params"]
    out = block.get("outputs", {})
    changed = False

    st.markdown("### 🖥️ AI Racks (hardware selection)")

    hw_keys = list(HARDWARE_CATALOG.keys())
    hw_labels = {k: HARDWARE_CATALOG[k]["label"] for k in hw_keys}
    new_hw = st.selectbox(
        "Compute platform",
        options=hw_keys,
        format_func=lambda k: hw_labels[k],
        index=hw_keys.index(p["hardware_key"]) if p["hardware_key"] in hw_keys else 0,
        key="rack_hw",
    )
    if new_hw != p["hardware_key"]:
        p["hardware_key"] = new_hw; changed = True

    hw = HARDWARE_CATALOG[p["hardware_key"]]
    st.caption(hw["caveat"])

    new_util = st.slider(
        "Time-averaged utilization",
        0.30, 0.95, float(p["utilization"]), step=0.05,
        key="rack_util",
        help="70% is realistic for steady inference serving; 90% only if queue never empties.",
    )
    if new_util != p["utilization"]:
        p["utilization"] = new_util; changed = True

    st.markdown("---")
    st.markdown("**Per-platform constants (from design_wiki):**")
    cols = st.columns(3)
    cols[0].metric("kW / rack (facility)", f"{hw['rack_kw']:.0f}")
    cols[1].metric("tokens/s per MW", f"{hw['tokens_per_sec_per_mw']:.1e}")
    cols[2].metric("PUE", f"{hw['pue']:.2f}")

    st.markdown("**Computed outputs:**")
    cols = st.columns(4)
    cols[0].metric("IT load", f"{out.get('it_mw', 0):.2f} MW")
    cols[1].metric("Facility draw", f"{out.get('facility_mw', 0):.2f} MW")
    cols[2].metric("Racks", f"{out.get('racks', 0)}")
    cols[3].metric("Tokens/sec", f"{out.get('tokens_per_sec', 0):.2e}")

    return changed


# ===========================================================================
#                               DC BUS (aggregator)
# ===========================================================================
def _editor_dc(design: Dict[str, Dict[str, Any]]) -> bool:
    block = design["dc"]
    p = block["params"]
    out = block.get("outputs", {})
    changed = False

    st.markdown("### ⚡ DC Bus (aggregator)")
    st.caption("Where PV, grid, and BESS feed the IT facility load. Tune the power share.")

    c1, c2 = st.columns(2)
    with c1:
        new_v = st.selectbox(
            "Distribution voltage",
            options=[0.48, 0.40, 0.80],
            index=[0.48, 0.40, 0.80].index(p["voltage_kv"]) if p["voltage_kv"] in [0.48, 0.40, 0.80] else 0,
            format_func=lambda v: {0.48: "480 V AC (baseline)",
                                   0.40: "400 V DC (OCP ORv3)",
                                   0.80: "800 V DC (Rubin / Kyber 2027)"}[v],
            key="dc_v",
            help="800 V DC is the NGDCI target for next-gen AI factories.",
        )
        if new_v != p["voltage_kv"]:
            p["voltage_kv"] = new_v; changed = True

    with c2:
        new_share = st.slider(
            "DC IT share of PV kWp",
            0.20, 0.60, float(p["it_load_share_of_pv_kwp"]), step=0.01,
            key="dc_share",
            help="0.35 = PV + BESS can serve DC most of daytime hours; higher = more grid reliance.",
        )
        if new_share != p["it_load_share_of_pv_kwp"]:
            p["it_load_share_of_pv_kwp"] = new_share; changed = True

    st.markdown("---")
    st.markdown("**Flows at this bus:**")
    cols = st.columns(3)
    cols[0].metric("PV AC inflow", f"{out.get('inflow_pv_ac_kw', 0):,.0f} kW")
    cols[1].metric("IT facility draw", f"{out.get('outflow_rack_kw', 0):,.0f} kW")
    cols[2].metric("WWTP net draw", f"{out.get('outflow_wwtp_kw', 0):,.0f} kW")

    st.markdown("**Revenue at four token-price points (per year):**")
    rev = out.get("revenue_per_year_usd", {})
    rev_cols = st.columns(len(PRICE_POINTS_USD_PER_MTOKEN))
    for col, price in zip(rev_cols, PRICE_POINTS_USD_PER_MTOKEN):
        v = rev.get(f"{price:.2f}", 0)
        col.metric(f"${price:.2f} / M tok", f"${v/1e6:.1f} M")

    return changed


# ===========================================================================
#                               WWTP LOAD
# ===========================================================================
def _editor_wwtp(design: Dict[str, Dict[str, Any]]) -> bool:
    block = design["wwtp"]
    p = block["params"]
    out = block.get("outputs", {})
    changed = False

    st.markdown("### 💧 WWTP Baseline Load")
    st.caption("Existing plant load already drawing from the feeder — we're adding on top.")

    c1, c2 = st.columns(2)
    with c1:
        new_mgd = st.slider(
            "Plant design flow (MGD)", 10.0, 150.0,
            float(p["mgd"]), step=1.0, key="wwtp_mgd",
        )
        if new_mgd != p["mgd"]:
            p["mgd"] = new_mgd; changed = True

        new_kw_per = st.slider(
            "kW per MGD", 50.0, 140.0,
            float(p["kw_per_mgd"]), step=1.0, key="wwtp_kw_per",
            help="BSM1-calibrated average is ~83 kW/MGD.",
        )
        if new_kw_per != p["kw_per_mgd"]:
            p["kw_per_mgd"] = new_kw_per; changed = True

    with c2:
        new_bio = st.slider(
            "Biogas CHP offset (kW)", 0.0, 2000.0,
            float(p["biogas_offset_kw"]), step=50.0, key="wwtp_bio",
            help="Biogas CHP provides constant offset; typical 500-1000 kW for ≥25 MGD plants.",
        )
        if new_bio != p["biogas_offset_kw"]:
            p["biogas_offset_kw"] = new_bio; changed = True

    st.markdown("---")
    cols = st.columns(2)
    cols[0].metric("Total plant load", f"{out.get('load_kw', 0):,.0f} kW")
    cols[1].metric("Net grid draw", f"{out.get('net_grid_draw_kw', 0):,.0f} kW")

    return changed


# ===========================================================================
#                               GRID
# ===========================================================================
def _editor_grid(design: Dict[str, Dict[str, Any]]) -> bool:
    block = design["grid"]
    p = block["params"]
    out = block.get("outputs", {})
    changed = False

    st.markdown("### 🔌 Utility Grid Interface")

    c1, c2 = st.columns(2)
    with c1:
        new_v = st.selectbox(
            "Service voltage",
            options=[12.47, 13.8, 25.0, 34.5, 69.0, 138.0],
            index=[12.47, 13.8, 25.0, 34.5, 69.0, 138.0].index(p["service_voltage_kv"]) if p["service_voltage_kv"] in [12.47, 13.8, 25.0, 34.5, 69.0, 138.0] else 2,
            format_func=lambda v: f"{v} kV",
            key="grid_v",
        )
        if new_v != p["service_voltage_kv"]:
            p["service_voltage_kv"] = new_v; changed = True

    with c2:
        new_xfmr = st.slider(
            "Existing transformer (MVA)", 1.0, 20.0,
            float(p["existing_xfmr_mva"]), step=0.5, key="grid_xfmr",
        )
        if new_xfmr != p["existing_xfmr_mva"]:
            p["existing_xfmr_mva"] = new_xfmr; changed = True

    st.markdown("---")
    headroom = out.get("headroom_kw", 0)
    cols = st.columns(3)
    cols[0].metric("Peak added",
                   f"{out.get('peak_added_kw', 0):,.0f} kW")
    cols[1].metric("Existing headroom",
                   f"{headroom:+,.0f} kW",
                   delta_color="normal" if headroom > 500 else "inverse")
    cols[2].metric("Upgrade cost",
                   f"${out.get('upgrade_cost_usd', 0):,.0f}")
    if out.get("upgrade_required"):
        st.warning(
            f"Transformer upgrade needed — headroom below 500 kW safety margin. "
            f"Budget ${p['transformer_upgrade_cost_usd']:,.0f} and "
            f"6-9 month lead time."
        )

    return changed


# ===========================================================================
#                               DISPATCH
# ===========================================================================
_DISPATCH: Dict[str, Callable[[Dict[str, Dict[str, Any]]], bool]] = {
    "pv":   _editor_pv,
    "inv":  _editor_inv,
    "bess": _editor_bess,
    "dc":   _editor_dc,
    "rack": _editor_rack,
    "wwtp": _editor_wwtp,
    "grid": _editor_grid,
}
