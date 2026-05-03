"""One-page site design report.

Called from the main app when the user clicks 📋 Report. Renders a formatted
executive summary of the current design: site params, PV, BESS, DC, grid,
revenue, CAPEX, assumptions, caveats. Copy-pastable to email; downloadable
as markdown.

Design principle: this is what an engineer would send to their boss or
drop into an RFP appendix. Professional tone, comprehensive numbers, clear
caveats. Not a chatbot transcript; a structured document.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

import streamlit as st

from stage1_5_wwtp_dc.design.archetypes import PRICE_POINTS_USD_PER_MTOKEN

from .blocks import HARDWARE_CATALOG


# ---------------------------------------------------------------------------
# CAPEX order-of-magnitude lookup (from design_wiki/capex/*)
# ---------------------------------------------------------------------------
CAPEX_RATES = {
    "pv_dollar_per_w_dc":   1.05,   # Lazard LCOE+ 2024 midpoint, single-axis bifacial
    "bess_dollar_per_kwh":  275.0,  # NREL ATB 2024 midpoint, 4-hour Li-ion
    "dc_facility_per_mw":   11_500_000.0,  # JLL/CBRE 2024 midpoint, liquid-cooled
    "gpu_per_mw":           30_000_000.0,  # Blackwell retail allocation, 2025
    "xfmr_upgrade_usd":     300_000.0,    # utility MV transformer service upgrade
}


# ---------------------------------------------------------------------------
# Build the report markdown
# ---------------------------------------------------------------------------
def build_report_markdown(design: Dict[str, Dict[str, Any]]) -> str:
    """Produce a multi-section markdown report from the current design."""
    pv_o  = design["pv"]["outputs"]
    pv_p  = design["pv"]["params"]
    inv_o = design["inv"]["outputs"]
    inv_p = design["inv"]["params"]
    bess_o = design["bess"]["outputs"]
    bess_p = design["bess"]["params"]
    rack_o = design["rack"]["outputs"]
    rack_p = design["rack"]["params"]
    wwtp_o = design["wwtp"]["outputs"]
    wwtp_p = design["wwtp"]["params"]
    dc_o = design["dc"]["outputs"]
    dc_p = design["dc"]["params"]
    grid_o = design["grid"]["outputs"]
    grid_p = design["grid"]["params"]

    hw = HARDWARE_CATALOG[rack_p["hardware_key"]]
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    # CAPEX
    pv_capex = pv_o["kwp_dc"] * 1000 * CAPEX_RATES["pv_dollar_per_w_dc"]
    bess_capex = bess_o["mwh"] * 1000 * CAPEX_RATES["bess_dollar_per_kwh"]
    dc_capex = rack_o["it_mw"] * CAPEX_RATES["dc_facility_per_mw"]
    gpu_capex = rack_o["it_mw"] * CAPEX_RATES["gpu_per_mw"]
    xfmr_capex = CAPEX_RATES["xfmr_upgrade_usd"] if grid_o["upgrade_required"] else 0
    total_capex = pv_capex + bess_capex + dc_capex + gpu_capex + xfmr_capex

    rev = dc_o.get("revenue_per_year_usd", {})
    rev_010 = rev.get("0.10", 0)
    simple_payback_years = total_capex / rev_010 if rev_010 > 0 else float("inf")

    # ------------------------- HEADER -------------------------
    md = [
        "# Behind-the-meter AI factory site design report",
        f"*Generated: {timestamp} · EnergyFlux Flowsheet Designer v1*",
        "",
        "---",
        "",
        "## Executive summary",
        "",
        f"A **{rack_o['it_mw']:.1f} MW IT-load AI inference facility** "
        f"colocated with a **{wwtp_p['mgd']:.0f} MGD** municipal wastewater "
        f"treatment plant. Behind-the-meter configuration: "
        f"no new grid interconnection required beyond a "
        f"{'required' if grid_o['upgrade_required'] else 'non-required'} "
        f"transformer upgrade. Site produces "
        f"**{pv_o['annual_mwh']:,.0f} MWh/yr** from "
        f"**{pv_o['kwp_dc']:,.0f} kWp** of {'bifacial ' if pv_p['bifacial'] else ''}"
        f"{pv_p['tracking']} PV on **{pv_p['area_acres']:.0f} acres** of "
        f"plant buffer land. Compute platform: **{hw['label']}** "
        f"({rack_o['racks']} racks, "
        f"~{rack_o['tokens_per_sec']:.2e} tokens/sec at full utilization).",
        "",
        "**Headline economics (first-pass, nameplate sizing):**",
        "",
        f"- CAPEX order-of-magnitude: **${total_capex/1e6:.1f} M**",
        f"- Revenue at $0.10/M tokens, 70% utilization: "
        f"**${rev_010/1e6:.1f} M/yr**",
        f"- Simple payback (revenue-only, no OPEX): "
        f"**{simple_payback_years:.1f} years**" if simple_payback_years < 100 else "- Simple payback: N/A",
        f"- Grid impact: **+{grid_o['peak_added_kw']:,.0f} kW** peak "
        f"(headroom {grid_o['headroom_kw']:+,.0f} kW on existing "
        f"{grid_p['existing_xfmr_mva']:.1f} MVA service)",
        "",
    ]

    # ------------------------- SITE -------------------------
    md += [
        "## Site parameters",
        "",
        "| Parameter | Value | Source |",
        "|---|---|---|",
        f"| WWTP design flow | {wwtp_p['mgd']:.0f} MGD | User-specified; EPA CWNS 2022 for context |",
        f"| Available buffer area | {pv_p['area_acres']:.1f} acres | User-specified (typical: ~90% of WWTP setback zone) |",
        f"| Site latitude | {pv_p['lat']:.2f}°N | Drives PV specific-yield zone |",
        f"| Plant electrical load | {wwtp_o['load_kw']:,.0f} kW | {wwtp_p['mgd']:.0f} MGD × {wwtp_p['kw_per_mgd']:.1f} kW/MGD |",
        f"| Biogas CHP offset | {wwtp_p['biogas_offset_kw']:,.0f} kW | Typical for ≥25 MGD plants |",
        f"| Net WWTP grid draw | {wwtp_o['net_grid_draw_kw']:,.0f} kW | Load − CHP offset |",
        "",
    ]

    # ------------------------- PV -------------------------
    md += [
        "## Photovoltaic array",
        "",
        "| Parameter | Value | Basis |",
        "|---|---|---|",
        f"| DC nameplate | **{pv_o['kwp_dc']:,.0f} kWp** | {pv_o['module_count']:,} × {pv_p['module_w']} W modules |",
        f"| Module technology | {pv_p['module_w']} W "
        f"{'bifacial ' if pv_p['bifacial'] else ''}{pv_p['tracking']} | "
        f"Industry workhorse 2025-2026 |",
        f"| Tracker GCR | {pv_p['gcr']:.2f} | Row pitch ≈ 2.4 m / {pv_p['gcr']:.2f} = "
        f"{2.4/max(pv_p['gcr'], 0.01):.1f} m |",
        f"| Modules per tracker | {pv_p['modules_per_tracker']} | 1500 V string config |",
        f"| String count | {pv_o['string_count']} strings | "
        f"{pv_o['module_count']:,} modules / {pv_o['modules_per_string']} per string |",
        f"| Central inverter count | {inv_o['count']} × {inv_p['kw_each']} kW | "
        f"ILR {inv_p['ilr']:.2f} |",
        f"| Annual AC energy | **{pv_o['annual_mwh']:,.0f} MWh/yr** | "
        f"{pv_o['specific_yield']:.0f} kWh/kWp/yr ({pv_o['zone']} zone) |",
        f"| Capacity factor | {pv_o['capacity_factor_pct']:.1f}% | From specific yield |",
        f"| PV CAPEX estimate | **${pv_capex/1e6:.1f} M** | "
        f"${CAPEX_RATES['pv_dollar_per_w_dc']:.2f}/W DC (Lazard 2024) |",
        "",
    ]

    # ------------------------- BESS -------------------------
    md += [
        "## Battery energy storage",
        "",
        "| Parameter | Value | Basis |",
        "|---|---|---|",
        f"| Nameplate energy | **{bess_o['mwh']:.2f} MWh** | "
        f"{rack_o['it_mw']:.2f} MW × {bess_p['duration_hours']:.0f} h |",
        f"| Max discharge | {bess_o['max_discharge_kw']:,.0f} kW | 1C at IT load |",
        f"| Max charge | {bess_o['max_charge_kw']:,.0f} kW | "
        f"Ratio {bess_p['chg_disch_ratio']:.2f} (peak-shaving default) |",
        f"| Chemistry / duration | Li-ion LFP, {bess_p['duration_hours']:.0f}-hour | "
        f"Industry default (covers TOU evening peak) |",
        f"| Round-trip efficiency | {bess_p['round_trip_eff']:.2%} | Modern LFP |",
        f"| BESS CAPEX estimate | **${bess_capex/1e6:.1f} M** | "
        f"${CAPEX_RATES['bess_dollar_per_kwh']:.0f}/kWh installed (NREL ATB 2024) |",
        "",
    ]

    # ------------------------- DC / RACK -------------------------
    md += [
        "## AI compute platform",
        "",
        "| Parameter | Value | Basis |",
        "|---|---|---|",
        f"| Hardware | **{hw['label']}** | {hw['caveat']} |",
        f"| IT load | **{rack_o['it_mw']:.2f} MW** | "
        f"{dc_p['it_load_share_of_pv_kwp']:.0%} of PV kWp |",
        f"| Facility load (incl cooling) | {rack_o['facility_mw']:.2f} MW | "
        f"PUE {rack_o['pue']:.2f} |",
        f"| Racks | **{rack_o['racks']}** | "
        f"IT load / {hw['rack_kw']:.0f} kW per rack |",
        f"| Peak tokens/second | {rack_o['tokens_per_sec']:.2e} | "
        f"At 100% utilization |",
        f"| Time-avg utilization | {rack_p['utilization']:.0%} | "
        f"Steady-state inference serving |",
        f"| DC facility CAPEX | ${dc_capex/1e6:.1f} M | "
        f"${CAPEX_RATES['dc_facility_per_mw']/1e6:.1f} M/MW IT, liquid-cooled |",
        f"| GPU hardware CAPEX | ${gpu_capex/1e6:.1f} M | "
        f"${CAPEX_RATES['gpu_per_mw']/1e6:.0f} M/MW IT (retail allocation) |",
        "",
    ]

    # ------------------------- GRID -------------------------
    md += [
        "## Grid interface",
        "",
        "| Parameter | Value | Status |",
        "|---|---|---|",
        f"| Service voltage | {grid_p['service_voltage_kv']:.1f} kV | "
        f"Existing WWTP service |",
        f"| Existing transformer | {grid_p['existing_xfmr_mva']:.1f} MVA "
        f"({grid_p['existing_xfmr_mva']*1000:,.0f} kW) | — |",
        f"| Peak added demand | {grid_o['peak_added_kw']:,.0f} kW | "
        f"= DC facility + BESS charge |",
        f"| Headroom | **{grid_o['headroom_kw']:+,.0f} kW** | "
        f"{'⚠️ **UPGRADE REQUIRED**' if grid_o['upgrade_required'] else '✓ Within existing capacity'} |",
    ]
    if grid_o["upgrade_required"]:
        md += [
            f"| Transformer upgrade cost | ${xfmr_capex:,.0f} | "
            f"6-9 month lead time, utility-led |",
        ]
    md += [""]

    # ------------------------- REVENUE -------------------------
    realized_tokens_yr = dc_o.get("realized_tokens_per_year", 0)
    realized_t_tokens = realized_tokens_yr / 1e12
    md += [
        "## Revenue outlook",
        "",
        f"Annual realized inference: **{realized_t_tokens:.1f} trillion tokens/year** "
        f"(at {rack_p['utilization']:.0%} utilization).",
        "",
        "| Token price ($/M tokens) | Annual revenue |",
        "|---|---|",
    ]
    for p in PRICE_POINTS_USD_PER_MTOKEN:
        v = rev.get(f"{p:.2f}", 0)
        highlight = "**" if abs(p - 0.10) < 1e-6 else ""
        md.append(f"| {highlight}${p:.2f}{highlight} | {highlight}${v/1e6:.1f} M/yr{highlight} |")
    md += [""]

    # ------------------------- TOTAL CAPEX + PAYBACK -------------------------
    md += [
        "## Total CAPEX and simple payback",
        "",
        "| Line item | Amount |",
        "|---|---|",
        f"| PV array (${CAPEX_RATES['pv_dollar_per_w_dc']:.2f}/W × {pv_o['kwp_dc']:,.0f} kWp) | ${pv_capex/1e6:.1f} M |",
        f"| BESS (${CAPEX_RATES['bess_dollar_per_kwh']:.0f}/kWh × {bess_o['mwh']:.1f} MWh) | ${bess_capex/1e6:.1f} M |",
        f"| DC facility (${CAPEX_RATES['dc_facility_per_mw']/1e6:.1f} M/MW × {rack_o['it_mw']:.1f} MW IT) | ${dc_capex/1e6:.1f} M |",
        f"| GPU hardware (${CAPEX_RATES['gpu_per_mw']/1e6:.0f} M/MW × {rack_o['it_mw']:.1f} MW) | ${gpu_capex/1e6:.1f} M |",
    ]
    if grid_o["upgrade_required"]:
        md.append(f"| Transformer upgrade | ${xfmr_capex/1e6:.2f} M |")
    md += [
        f"| **Total (order-of-magnitude)** | **${total_capex/1e6:.1f} M** |",
        "",
        f"Simple payback at $0.10/M tokens: **{simple_payback_years:.1f} years** "
        f"(revenue-only; does not subtract OPEX, electricity, or financing).",
        "",
    ]

    # ------------------------- ASSUMPTIONS + CAVEATS -------------------------
    md += [
        "## Key assumptions",
        "",
        f"- **PV**: {pv_p['module_w']} W "
        f"{'bifacial ' if pv_p['bifacial'] else ''}modules, "
        f"{pv_p['tracking']}, GCR {pv_p['gcr']:.2f}, "
        f"performance ratio {pv_p['performance_ratio']:.2f}",
        f"- **Specific yield**: {pv_o['specific_yield']:.0f} kWh/kWp/yr "
        f"(NREL PVWatts {pv_o['zone']} zone baseline)",
        f"- **WWTP load model**: {wwtp_p['kw_per_mgd']:.1f} kW/MGD "
        f"(calibrated from BSM1 ODE at 30 MGD)",
        f"- **Hardware**: {hw['label']} — {hw['caveat']}",
        f"- **Utilization**: {rack_p['utilization']:.0%} "
        f"(steady-state inference; lower under low-traffic hours)",
        f"- **BESS**: {bess_p['duration_hours']:.0f}-hour Li-ion LFP, "
        f"{bess_p['round_trip_eff']:.2%} round-trip",
        f"- **Revenue model**: tokens × time-avg utilization × price per M tokens",
        "",
        "## Caveats (what this first-pass sizing does NOT capture)",
        "",
        "- **Dynamic behavior**: no 8,760-hour time-series simulation; steady-state only. Cloudy-day / heatwave / aeration-spike stress testing deferred to the dynamic-validation workstream.",
        "- **Operations optimization**: no MPC / dispatch optimization; revenue assumes simple utilization. Flexible-operation MPC (pyomo) with latency-tier demand response deferred.",
        "- **Weather variability**: specific yield is an annual average. Monthly / seasonal shortfalls not modeled.",
        "- **OPEX & financing**: payback is revenue-only (gross). Actual payback adds ~$1.5–3 M/yr O&M, electricity for BESS charging and grid imports, and financing costs at 8–12% WACC for utility-scale project debt.",
        "- **Token price volatility**: $0.10 / M tokens is the midpoint; inference pricing has fallen ~60% year-over-year in 2023–2025 and could continue. Sensitivity runs at $0.05 and $0.20 are shown above.",
        "- **Hardware version risk**: GPU pricing and performance depend on the generation (Blackwell, Vera Rubin, etc.). Numbers reflect the selected platform only.",
        "- **Permitting**: assumes behind-the-meter classification holds. State-by-state interconnection rules may require a higher study tier if peak-added exceeds 5 MW in some jurisdictions.",
        "",
        "---",
        "",
        f"*Report produced by `stage1_5_wwtp_dc.apps.flowsheet.report`. "
        f"Source code: `stage1_5_wwtp_dc/apps/flowsheet/`. "
        f"Citations backing every number are in `stage1_5_wwtp_dc/design_wiki/`.*",
    ]

    return "\n".join(md)


# ---------------------------------------------------------------------------
# Streamlit renderer
# ---------------------------------------------------------------------------
def render_report(design: Dict[str, Dict[str, Any]]) -> None:
    """Render the one-page report inside a Streamlit expander. Called from
    the main app when the user clicks 📋 Report in the sidebar."""
    md = build_report_markdown(design)

    # Show the report body
    st.markdown(md)

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.download_button(
        "⬇️ Download as .md",
        data=md,
        file_name=f"energyflux_site_report_{datetime.utcnow().strftime('%Y%m%d')}.md",
        mime="text/markdown",
        use_container_width=True,
    )
    col2.download_button(
        "⬇️ Download as .txt",
        data=md,
        file_name=f"energyflux_site_report_{datetime.utcnow().strftime('%Y%m%d')}.txt",
        mime="text/plain",
        use_container_width=True,
    )
    if col3.button("✖ Close report", use_container_width=True):
        st.session_state["_show_report"] = False
        st.rerun()
