"""LLM copilot panel — demoted from driver to sidekick.

The flowsheet UI puts the engineer in control (click block → edit params →
system recomputes). The copilot's job is to help when asked:

* Explain a number in the current design ("why 16 racks?")
* Suggest a parameter change ("what if I switch to Rubin?")
* Cite the wiki entry behind a design choice
* Answer open-ended questions ("is 23 acres enough for 5 MW?")

Crucially, the copilot is **fed the current design as context on every turn**
so its answers reflect what the engineer is actually looking at, not a
hypothetical.

Implementation style: borrowed from Claude Code — dark, compact, streaming,
tool-call expandable. Not a full-width chat page; fits in a side column.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import streamlit as st

from stage1_5_wwtp_dc.design.archetypes import PRICE_POINTS_USD_PER_MTOKEN


# ---------------------------------------------------------------------------
# System prompt for the copilot — compact, design-aware
# ---------------------------------------------------------------------------
COPILOT_SYSTEM_PROMPT = """\
You are a senior Solutions Architect copilot embedded in an AI-factory design
tool. The engineer is driving — you assist, you don't lead.

You see a TEXT SNAPSHOT of their current design every turn below this prompt.
It lists every parameter AND every derived output, PLUS the raw arithmetic
ingredients behind key computed values. Trust the snapshot completely.

CRITICAL RULES (follow in order):

1. **ANSWER FIRST, RETRIEVE ONLY IF NEEDED.** Most questions can be
   answered directly from the snapshot. Only call `retrieve` if the
   question is about design RATIONALE ("why X over Y?") AND the answer
   is not already in the snapshot text. Most questions need ZERO tool calls.

2. **MAXIMUM ONE `retrieve` CALL PER TURN.** If the first retrieve doesn't
   find what you need, DO NOT try again with a different query. Instead,
   answer with what you have plus: "My wiki doesn't have that specific
   topic — I have entries on [list what is there]. Want me to reason from
   first principles instead?"

3. **DO THE ARITHMETIC YOURSELF.** Q: "How is headroom -578 kW calculated?"
   A: "Existing transformer = 4,000 kW. Peak added = 4,578 kW.
       Headroom = 4,000 − 4,578 = −578 kW." One tool call, done.

4. **Do NOT call `calc_annual_yield` or `design_pv_array` for arithmetic
   questions on the current design.** Those tools are for "what if I
   changed X" scenarios, not explaining values already in the snapshot.

5. **If the question is outside the EnergyFlux / AI-factory scope**
   (e.g. "how do I design a WWTP?" — we don't size treatment processes,
   only colocation sites), say so directly: "That's outside this tool's
   scope; it sizes colocated AI factories, not the WWTP itself. For that
   you'd want WEF MOP-8 or BSM1 references." DO NOT burn tool calls
   looking for content that isn't there.

6. **Be short** — 2-5 sentences for routine questions.

7. **Suggest one concrete change at a time** when asked for improvements.
"""


# ---------------------------------------------------------------------------
# Design → compact text summary (fed to the LLM every turn)
# ---------------------------------------------------------------------------
def _summarize_design(design: Dict[str, Dict[str, Any]]) -> str:
    """Compact text summary of the design state for the LLM's context.

    Includes BOTH the final computed values AND the arithmetic ingredients
    behind every non-trivial derived number. Mental model: the engineer
    should be able to ask "how is X calculated" for any X in the KPI strip
    and the LLM should be able to answer without calling any tool — the
    ingredients are right here.
    """
    pv = design["pv"]["outputs"]
    inv = design["inv"]["outputs"]
    bess = design["bess"]["outputs"]
    dc = design["dc"]["outputs"]
    rack = design["rack"]["outputs"]
    wwtp = design["wwtp"]["outputs"]
    grid = design["grid"]["outputs"]

    pv_p = design["pv"]["params"]
    inv_p = design["inv"]["params"]
    bess_p = design["bess"]["params"]
    dc_p = design["dc"]["params"]
    rack_p = design["rack"]["params"]
    wwtp_p = design["wwtp"]["params"]
    grid_p = design["grid"]["params"]

    rev = dc.get("revenue_per_year_usd", {})
    rev_line = ""
    if rev:
        parts = [f"${float(rev[f'{p:.2f}']) / 1e6:.1f}M @ ${p:.2f}/Mtok"
                 for p in PRICE_POINTS_USD_PER_MTOKEN]
        rev_line = "  Revenue: " + "  |  ".join(parts)

    existing_xfmr_kw = grid_p["existing_xfmr_mva"] * 1000.0
    peak_added = grid.get("peak_added_kw", 0)
    rack_facility_kw = rack.get("facility_mw", 0) * 1000.0
    bess_max_charge = bess.get("max_charge_kw", 0)

    lines = [
        "CURRENT DESIGN SNAPSHOT",
        "=" * 50,
        "",
        f"SITE: {pv_p['area_acres']} acres @ {pv_p['lat']}°N "
        f"(zone={pv.get('zone')})",
        "",
        "PV BLOCK:",
        f"  params: module_w={pv_p['module_w']}W, tracking={pv_p['tracking']}, "
        f"bifacial={pv_p['bifacial']}, GCR={pv_p['gcr']}, PR={pv_p['performance_ratio']}",
        f"  kwp_dc = {pv.get('kwp_dc', 0):,.0f} kWp "
        f"(= module_count {pv.get('module_count', 0):,} × {pv_p['module_w']}W / 1000)",
        f"  annual_mwh = {pv.get('annual_mwh', 0):,.0f} MWh "
        f"(= {pv.get('kwp_dc', 0):,.0f} kWp × {pv.get('specific_yield', 0):.0f} kWh/kWp/yr / 1000)",
        f"  capacity_factor = {pv.get('capacity_factor_pct', 0):.2f}%",
        "",
        "INVERTER BLOCK:",
        f"  params: kw_each={inv_p['kw_each']}kW, ILR={inv_p['ilr']}, "
        f"efficiency={inv_p['efficiency']}",
        f"  count = {inv.get('count', 0)} "
        f"(= ceil({pv.get('kwp_dc', 0):,.0f} kWp / ILR {inv_p['ilr']} / {inv_p['kw_each']}kW))",
        f"  total_kw_ac = {inv.get('total_kw_ac', 0):,.0f} kW",
        f"  output_kw_ac = {inv.get('output_kw_ac', 0):,.0f} kW "
        f"(= total_kw_ac × efficiency {inv_p['efficiency']})",
        "",
        "RACK BLOCK (AI compute):",
        f"  hardware: {rack.get('hardware_label')} "
        f"({rack.get('rack_kw', 0):.0f} kW/rack, PUE {rack.get('pue')}, "
        f"{rack.get('tokens_per_sec_per_mw', rack_p.get('tokens_per_sec_per_mw', 0)) if False else ''}"
        f"tokens_per_sec_per_mw from wiki)",
        f"  it_mw = {rack.get('it_mw', 0):.3f} MW "
        f"(= dc.it_load_share_of_pv_kwp {dc_p['it_load_share_of_pv_kwp']} "
        f"× pv.kwp_dc {pv.get('kwp_dc', 0):,.0f} / 1000)",
        f"  facility_mw = {rack.get('facility_mw', 0):.3f} MW "
        f"(= it_mw × PUE {rack.get('pue')})",
        f"  racks = {rack.get('racks', 0)} "
        f"(= round(it_mw {rack.get('it_mw', 0):.3f} × 1000 / "
        f"rack_kw {rack.get('rack_kw', 0):.0f}))",
        f"  tokens_per_sec = {rack.get('tokens_per_sec', 0):.3e}",
        "",
        "BESS BLOCK:",
        f"  params: duration_hours={bess_p['duration_hours']}h, "
        f"chg_disch_ratio={bess_p['chg_disch_ratio']}, "
        f"sizing_basis={bess_p['sizing_basis']}",
        f"  mwh = {bess.get('mwh', 0):.2f} MWh "
        f"(= it_mw {rack.get('it_mw', 0):.3f} × duration_hours {bess_p['duration_hours']})",
        f"  max_discharge_kw = {bess.get('max_discharge_kw', 0):,.0f} kW "
        f"(= it_mw × 1000)",
        f"  max_charge_kw = {bess_max_charge:,.0f} kW "
        f"(= max_discharge × chg_disch_ratio {bess_p['chg_disch_ratio']})",
        "",
        "WWTP BLOCK:",
        f"  params: mgd={wwtp_p['mgd']}, kw_per_mgd={wwtp_p['kw_per_mgd']}, "
        f"biogas_offset_kw={wwtp_p['biogas_offset_kw']}",
        f"  load_kw = {wwtp.get('load_kw', 0):,.1f} kW "
        f"(= mgd × kw_per_mgd)",
        f"  net_grid_draw_kw = {wwtp.get('net_grid_draw_kw', 0):,.0f} kW "
        f"(= load_kw − biogas_offset_kw)",
        "",
        "DC BUS BLOCK:",
        f"  voltage = {dc_p['voltage_kv']} kV ({dc_p['voltage_kv']*1000:.0f} V)",
        f"  inflow_pv_ac_kw = {dc.get('inflow_pv_ac_kw', 0):,.0f} kW",
        f"  outflow_rack_kw = {dc.get('outflow_rack_kw', 0):,.0f} kW",
        f"  outflow_wwtp_kw = {dc.get('outflow_wwtp_kw', 0):,.0f} kW",
        "",
        "GRID BLOCK:",
        f"  params: existing_xfmr_mva={grid_p['existing_xfmr_mva']} "
        f"(= {existing_xfmr_kw:,.0f} kW), "
        f"service_voltage_kv={grid_p['service_voltage_kv']}",
        f"  peak_added_kw = {peak_added:,.0f} kW "
        f"(= rack.facility_mw×1000 {rack_facility_kw:,.0f} + "
        f"bess.max_charge_kw {bess_max_charge:,.0f})",
        f"  headroom_kw = {grid.get('headroom_kw', 0):+,.0f} kW "
        f"(= existing_xfmr_kw {existing_xfmr_kw:,.0f} − peak_added_kw {peak_added:,.0f})",
        f"  upgrade_required = {grid.get('upgrade_required')} "
        f"(True if headroom < 500 kW safety margin)",
        f"  upgrade_cost_usd = ${grid.get('upgrade_cost_usd', 0):,.0f} "
        f"(if upgrade needed)",
        "",
        "REVENUE (annual, at 4 token-price points):",
        rev_line,
    ]
    return "\n".join(line for line in lines if line is not None)


def _selected_block_note(selected: Optional[str], design: Dict[str, Dict[str, Any]]) -> str:
    if not selected:
        return "The engineer hasn't selected a specific block right now."
    block = design[selected]
    return (
        f"The engineer is currently editing the **{block['label']}** block "
        f"(kind={block['kind']}). Bias your answers toward this component "
        f"unless they ask about something else."
    )


# ---------------------------------------------------------------------------
# Panel renderer
# ---------------------------------------------------------------------------
def render_copilot_panel(
    design: Dict[str, Dict[str, Any]],
    selected_block: Optional[str],
    api_key: str,
    model: str,
    key_prefix: str = "copilot",
) -> None:
    """Render the copilot as a panel with chat input AT THE TOP, so users
    never have to scroll to find where to type. History + sources below."""
    if not api_key:
        st.info(
            "Copilot is offline — add `NVIDIA_API_KEY=nvapi-...` to `.env`. "
            "The flowsheet runs fine without it.",
            icon="ℹ️",
        )
        return

    hist_key = f"{key_prefix}_history"
    tools_key = f"{key_prefix}_tools"
    if hist_key not in st.session_state:
        st.session_state[hist_key] = []
    if tools_key not in st.session_state:
        st.session_state[tools_key] = []

    # ═══ TOP: chat input — FIRST thing user sees ══════════════════════════
    st.markdown(
        "<div style='color:#FFD166; font-weight:600; margin-bottom:4px;'>"
        "💬 Ask me about this design ↓"
        "</div>",
        unsafe_allow_html=True,
    )
    user_msg = st.chat_input(
        "e.g. 'how is -578 kW headroom calculated?'",
        key=f"{key_prefix}_input",
    )

    # Quick-action buttons right under input — compact, stacked
    quick_prompts: List[str] = []
    qc1, qc2 = st.columns(2)
    if qc1.button("📊 Explain numbers",
                  use_container_width=True, key=f"{key_prefix}_qa1",
                  help="Ask the copilot to walk through the 3 most important numbers"):
        quick_prompts.append(
            "Explain the 3 most important numbers in my current design and "
            "which parameter each one is driven by. Keep it to 4 sentences."
        )
    if qc2.button("💡 Suggest change",
                  use_container_width=True, key=f"{key_prefix}_qa2",
                  help="Ask for one concrete parameter change suggestion"):
        quick_prompts.append(
            "Propose ONE specific parameter change I should consider, with "
            "the quantified tradeoff. Keep it to 3 sentences."
        )

    effective_msg = user_msg or (quick_prompts[0] if quick_prompts else "")

    # ═══ MIDDLE: process input (if any) ═══════════════════════════════════
    if effective_msg:
        st.session_state[hist_key].append({"role": "user", "content": effective_msg})
        with st.spinner("Thinking…"):
            reply, tool_log = _call_copilot(
                user_msg=effective_msg,
                design=design,
                selected_block=selected_block,
                history=st.session_state[hist_key][:-1],
                api_key=api_key,
                model=model,
            )
        st.session_state[hist_key].append({"role": "assistant", "content": reply})
        st.session_state[tools_key].append(tool_log)
        st.rerun()

    # ═══ BOTTOM: conversation history ═════════════════════════════════════
    st.markdown("---")
    if st.session_state[hist_key]:
        st.markdown(
            f"<div style='color:#9AA6B2; font-size:0.82rem;'>"
            f"Conversation ({len(st.session_state[hist_key])} messages):"
            f"</div>",
            unsafe_allow_html=True,
        )
        with st.container(border=True, height=380):
            # Newest at TOP — reverse order so user sees latest answer first
            msgs = list(reversed(st.session_state[hist_key]))
            for msg in msgs[:16]:
                role_label = "**🧑 You**" if msg["role"] == "user" else "**🤖 Copilot**"
                st.markdown(f"{role_label}\n\n{msg['content']}")
                st.markdown("---")

        # Tool calls from most recent assistant turn
        if st.session_state[tools_key] and st.session_state[tools_key][-1]:
            with st.expander(
                f"🔎 Sources for last answer ({len(st.session_state[tools_key][-1])} tool calls)",
                expanded=False,
            ):
                for i, entry in enumerate(st.session_state[tools_key][-1], 1):
                    st.markdown(f"**{i}. `{entry['tool']}`**")
                    st.code(json.dumps(entry["args"], indent=2), language="json")

        if st.button("🗑️ Clear conversation", key=f"{key_prefix}_clear",
                     use_container_width=True):
            st.session_state[hist_key] = []
            st.session_state[tools_key] = []
            st.rerun()
    else:
        st.caption(
            "No messages yet. Type above, or click one of the quick-action "
            "buttons. The copilot sees whatever block you've selected in "
            "the main area."
        )


def _call_copilot(
    user_msg: str,
    design: Dict[str, Dict[str, Any]],
    selected_block: Optional[str],
    history: List[Dict[str, Any]],
    api_key: str,
    model: str,
) -> tuple[str, List[Dict[str, Any]]]:
    """One copilot turn. Uses the same tool-calling loop from design.llm."""
    try:
        from stage1_5_wwtp_dc.design.llm import (
            ALL_TOOL_SCHEMAS, make_client, run_tool_loop,
        )
    except Exception as e:  # noqa: BLE001
        return f"❌ LLM import failed: {e}", []

    try:
        client, mdl = make_client(api_key=api_key, model=model)
    except RuntimeError as e:
        return f"❌ {e}", []

    system_msg = (
        COPILOT_SYSTEM_PROMPT
        + "\n\n"
        + _selected_block_note(selected_block, design)
        + "\n\n"
        + _summarize_design(design)
    )

    messages = [{"role": "system", "content": system_msg}]
    for turn in history:
        messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user", "content": user_msg})

    try:
        _updated, text, tool_log = run_tool_loop(
            client=client, model=mdl, messages=messages, max_steps=4,
        )
    except Exception as e:  # noqa: BLE001
        return f"❌ NIM call failed: `{e}`", []

    return text, tool_log
