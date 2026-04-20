"""Blog 2 main demo — GenAI-assisted AI factory site design.

LLM (NVIDIA NIM) drives a conversation; it calls PV / RAG / sizing tools;
the right-hand panel shows live sizing cards + a parcel layout plot; every
turn lists which wiki files and tool calls grounded the answer.

Run locally:
    streamlit run stage1_5_wwtp_dc/apps/blog2_genai_app.py

Streamlit Cloud entry point:
    stage1_5_wwtp_dc/apps/blog2_genai_app.py

Secrets (in Streamlit Cloud settings, or .env locally):
    NVIDIA_NIM_API_KEY = "<free key from build.nvidia.com>"

If no key is set, the app falls back to "mock mode": sidebar inputs drive
``design.pv_tools`` + ``design.sizing`` directly, so the UI still renders
meaningful output for a reader who just wants to see the math.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import streamlit as st

# Make the stage1_5_wwtp_dc package importable when Streamlit runs this file.
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Load .env so NVIDIA_API_KEY is picked up without manual export.
# python-dotenv is already a dependency via requirements-dev.txt; if missing
# at runtime we silently skip (user can still paste the key in the sidebar).
try:
    from dotenv import load_dotenv
    load_dotenv(REPO_ROOT / ".env")
except ImportError:
    pass

from stage1_5_wwtp_dc.design.pv_tools import (  # noqa: E402
    array_layout, calc_annual_yield, compare_pv_technologies,
    design_pv_array, MODULE_CATALOG, KWP_PER_ACRE,
)
from stage1_5_wwtp_dc.design.rag import get_retriever  # noqa: E402
from stage1_5_wwtp_dc.design.sizing import size_site  # noqa: E402
from stage1_5_wwtp_dc.design.archetypes import ARCHETYPES, ARCHETYPE_LABELS  # noqa: E402


# =============================================================================
# Helpers (defined before the UI so the Streamlit script can call them top-down)
# =============================================================================
def render_tool_result(entry: dict) -> None:
    """Pretty-print one tool call's result in the sources panel."""
    tool = entry["tool"]
    result = entry["result"]
    if tool == "retrieve":
        hits = (result or {}).get("hits", [])
        for h in hits:
            st.markdown(f"📄 **[{h['title']}]** `{h['path']}` — score {h['score']:.2f}")
            st.caption(h.get("excerpt", "")[:300])
    else:
        st.json(result, expanded=False)


def run_live(user_prompt: str, api_key: str, model_name: str,
             prior_messages: list) -> tuple[str, list]:
    """Real NIM call with the full tool loop. Returns (text, tool_log)."""
    try:
        from stage1_5_wwtp_dc.design.llm import (
            SYSTEM_PROMPT, make_client, run_tool_loop,
        )
    except Exception as e:  # noqa: BLE001
        return (f"❌ LLM import failed: {e}\n\n"
                f"If `openai` is missing, add it to requirements-deploy.txt.", [])

    try:
        client, mdl = make_client(api_key=api_key, model=model_name)
    except RuntimeError as e:
        return f"❌ {e}", []

    # Build history: system prompt + all prior user/assistant turns + new user msg.
    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in prior_messages:
        history.append({"role": m["role"], "content": m["content"]})
    history.append({"role": "user", "content": user_prompt})

    try:
        _updated, final_text, tool_log = run_tool_loop(
            client=client,
            model=mdl,
            messages=history,
            max_steps=6,
        )
    except Exception as e:  # noqa: BLE001
        return (f"❌ NIM call failed: `{e}`. Check API key or rate limits.", [])

    return final_text, tool_log


def run_mock(user_prompt: str, snapshot: dict) -> tuple[str, list]:
    """No-LLM fallback: just rephrase the sidebar state."""
    d, y = snapshot["design"], snapshot["yield"]
    reply = (
        f"_(mock mode — no NVIDIA NIM key detected, so I'm summarizing the "
        f"sidebar inputs instead of running the LLM.)_\n\n"
        f"**Your question:** {user_prompt}\n\n"
        f"Based on your sidebar inputs:\n"
        f"- **PV nameplate:** {d['kwp_dc']:,.0f} kWp DC "
        f"({d['module_count']:,} × {d['module_w']} W modules, "
        f"{d['tracking']})\n"
        f"- **Annual yield:** {y['annual_mwh']:,.0f} MWh at "
        f"{y['capacity_factor_pct']:.1f}% CF (zone: `{y['zone']}`)\n"
        f"- **Inverters:** {d['inverter_count']}× {d['inverter_kw_each']} kW central\n"
        f"- **Footprint:** {d['dimensions_m']['width_m']:.0f} × "
        f"{d['dimensions_m']['depth_m']:.0f} m on {d['area_used_acres']:.1f} acres\n\n"
        f"Paste an NVIDIA NIM key in the sidebar (free at build.nvidia.com) "
        f"to turn on the real tool-calling assistant."
    )
    return reply, []


def snapshot_from_args(area_acres: float, lat: float, module_w: int,
                       tracking: str, bifacial: bool) -> dict:
    design = design_pv_array(
        area_acres=area_acres, module_w=module_w,
        tracking=tracking, bifacial=bifacial,
    )
    yld = calc_annual_yield(
        kwp_dc=design["kwp_dc"], lat=lat,
        tracking=tracking, bifacial=bifacial,
    )
    return {"design": design, "yield": yld, "layout": array_layout(design)}


def maybe_update_snapshot_from_log(tool_log: list, lat: float) -> None:
    """If the LLM ran design_pv_array this turn, refresh the side card."""
    for entry in tool_log:
        if entry["tool"] == "design_pv_array" and isinstance(entry.get("result"), dict):
            design = entry["result"]
            tracking_for_yield = design["tracking"].replace("_bifacial", "")
            y = calc_annual_yield(
                kwp_dc=design["kwp_dc"], lat=lat,
                tracking=tracking_for_yield, bifacial=design["bifacial"],
            )
            st.session_state.design_snapshot = {
                "design": design, "yield": y, "layout": array_layout(design),
            }
            return


# =============================================================================
# Page config
# =============================================================================
st.set_page_config(
    page_title="EnergyFlux — AI-Assisted Site Design",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("# GenAI-assisted design of a behind-the-meter AI factory")
st.caption(
    "Pick a site, have a conversation with the design assistant, watch the "
    "PV / BESS / DC numbers update live. Every assertion is grounded in "
    "either a `pvlib`-style tool call or a retrieved wiki entry — sources "
    "shown at the bottom of each turn."
)


# =============================================================================
# Sidebar
# =============================================================================
with st.sidebar:
    st.markdown("### Site inputs")
    area_acres = st.slider("Available buffer area (acres)", 5, 60, 23, step=1,
                           help="90% of WWTP buffer zone after access roads.")
    lat = st.slider("Site latitude (°N)", 24.0, 49.0, 30.27, step=0.1,
                    help="Default: Austin TX. Affects specific yield zone.")
    module_w = st.selectbox("Module wattage", sorted(MODULE_CATALOG.keys()),
                            index=sorted(MODULE_CATALOG.keys()).index(580))
    tracking = st.selectbox(
        "Tracking",
        ["single_axis", "fixed_tilt", "dual_axis"],
        index=0,
    )
    bifacial = st.checkbox("Bifacial modules", value=True)

    st.markdown("---")
    st.markdown("### NVIDIA NIM")
    api_key_input = st.text_input(
        "API key (free at build.nvidia.com)",
        value=os.getenv("NVIDIA_API_KEY", os.getenv("NVIDIA_NIM_API_KEY", "")),
        type="password",
        help="Without a key the app stays in mock mode. Reads NVIDIA_API_KEY from .env.",
    )
    model = st.selectbox(
        "Model",
        [
            "meta/llama-3.1-70b-instruct",       # default; reliable, small credit cost
            "meta/llama-3.1-405b-instruct",      # higher quality, ~6x the credits
            "openai/gpt-oss-120b",               # NVIDIA's replacement for deprecated Nemotron
            "deepseek-ai/deepseek-v3",           # strong alt; more credits
        ],
        index=0,
        help="Nemotron 70B was deprecated on 2026-04-15; openai/gpt-oss-120b is NVIDIA's recommended replacement.",
    )
    live_mode = bool(api_key_input.strip())
    mode_label = "🟢 live" if live_mode else "🟠 mock"
    st.caption(f"Mode: **{mode_label}**")

    st.markdown("---")
    st.markdown("### About")
    st.markdown(
        "Blog 2 companion. See `ROADMAP.md` for the 9-blog series, or "
        "`BLOG2_PRD.md` for this demo's scope. Source under "
        "`stage1_5_wwtp_dc/design/`."
    )


# =============================================================================
# Session state + baseline snapshot
# =============================================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "tool_log" not in st.session_state:
    st.session_state.tool_log = []
if "design_snapshot" not in st.session_state:
    st.session_state.design_snapshot = None

# Always keep a fresh snapshot in sync with the sidebar for the "current view".
st.session_state.design_snapshot = snapshot_from_args(
    area_acres, lat, module_w, tracking, bifacial,
)


# =============================================================================
# Main two-column layout
# =============================================================================
col_chat, col_cards = st.columns([3, 2], gap="large")


# ------------------------- RIGHT: live cards + viz --------------------------
with col_cards:
    snap = st.session_state.design_snapshot
    design, yld, layout = snap["design"], snap["yield"], snap["layout"]

    st.markdown("### Current design snapshot")
    c1, c2 = st.columns(2)
    c1.metric("PV nameplate", f"{design['kwp_dc']:,.0f} kWp")
    c2.metric("Modules", f"{design['module_count']:,}")
    c3, c4 = st.columns(2)
    c3.metric("Annual energy", f"{yld['annual_mwh']:,.0f} MWh/yr")
    c4.metric("Capacity factor", f"{yld['capacity_factor_pct']:.1f}%")
    c5, c6 = st.columns(2)
    c5.metric("Inverters", f"{design['inverter_count']}× {design['inverter_kw_each']} kW")
    c6.metric("Strings", f"{design['string_count']}")

    st.caption(
        f"Tracking: `{design['tracking']}`  •  Module: {design['module_w']} W "
        f"({MODULE_CATALOG[design['module_w']]['technology']})  •  "
        f"Zone: `{yld['zone']}`  •  PR: {yld['performance_ratio']:.2f}"
    )

    # Parcel layout viz
    fig, ax = plt.subplots(figsize=(6, 3.2), dpi=110)
    for label_, key, color in [
        ("Parcel",         "parcel",         "#D9DEE5"),
        ("PV array",       "active_array",   "#1F4E79"),
        ("Inverter strip", "inverter_strip", "#E8A33D"),
    ]:
        r = layout[key]
        ax.add_patch(plt.Rectangle(
            (r["x"], r["y"]), r["w"], r["h"],
            facecolor=color, edgecolor="white", linewidth=1.2,
            label=label_,
        ))
    ax.set_xlim(-10, layout["parcel"]["w"] + 10)
    ax.set_ylim(-10, layout["parcel"]["h"] + 10)
    ax.set_aspect("equal")
    ax.set_xlabel("width (m)")
    ax.set_ylabel("depth (m)")
    ax.legend(loc="upper right", fontsize=8)
    ax.set_title(
        f"{design['area_used_acres']:.1f} ac parcel  →  {design['kwp_dc']:,.0f} kWp",
        fontsize=10,
    )
    ax.grid(alpha=0.2)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    # Archetype-matched full site sizing (optional drill-down)
    st.markdown("---")
    with st.expander("📐 Archetype-matched full site sizing"):
        # Pick the archetype whose implied DC IT matches this PV.
        implied_dc_mw = 0.35 * design["kwp_dc"] / 1000.0
        arch_names = sorted(ARCHETYPES.keys(), key=lambda n: ARCHETYPES[n]["mgd"])
        matched = min(
            arch_names,
            key=lambda n: abs(
                0.35 * ARCHETYPES[n]["buffer_acres"] * 0.9 * 317.0 / 1000 - implied_dc_mw
            ),
        )
        report = size_site(matched)
        st.caption(
            f"Closest match ({implied_dc_mw:.2f} MW DC IT implied): "
            f"**{ARCHETYPE_LABELS[matched]}**"
        )
        st.json(report, expanded=False)


# ------------------------- LEFT: chat interface ----------------------------
with col_chat:
    st.markdown("### Conversation")

    # Starter prompts
    if not st.session_state.messages:
        with st.container(border=True):
            st.markdown("**Try one of these to get started:**")
            b1, b2, b3 = st.columns(3)
            if b1.button("45 MGD site in Austin TX", use_container_width=True):
                st.session_state.prefill = (
                    "I have a 45 MGD WWTP outside Austin TX with about 23 acres "
                    "of buffer. What's the biggest AI factory I can build there?"
                )
                st.rerun()
            if b2.button("Compare tracking options", use_container_width=True):
                st.session_state.prefill = (
                    "On 23 acres at 30°N, how much better is single-axis tracking "
                    "vs fixed tilt? Include bifacial."
                )
                st.rerun()
            if b3.button("Blackwell vs Rubin", use_container_width=True):
                st.session_state.prefill = (
                    "For the 30 MGD archetype, compare Blackwell GB200 against "
                    "Vera Rubin NVL144 on the same DC power envelope."
                )
                st.rerun()

    # Render existing conversation
    _pad = len(st.session_state.messages) - len(st.session_state.tool_log)
    padded_tool_log = st.session_state.tool_log + [[]] * max(0, _pad)
    for m, tc_log in zip(st.session_state.messages, padded_tool_log):
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            if m["role"] == "assistant" and tc_log:
                with st.expander(f"🔍  Sources used ({len(tc_log)} tool calls)"):
                    for i, entry in enumerate(tc_log, 1):
                        st.markdown(f"**{i}. `{entry['tool']}`**")
                        st.code(json.dumps(entry["args"], indent=2), language="json")
                        with st.container(border=True):
                            render_tool_result(entry)

    # Input
    prefill = st.session_state.pop("prefill", "")
    prompt = st.chat_input("Tell me about your site...") or prefill or ""

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                if live_mode:
                    reply, tool_log = run_live(
                        prompt, api_key_input, model,
                        prior_messages=st.session_state.messages[:-1],
                    )
                else:
                    reply, tool_log = run_mock(
                        prompt, st.session_state.design_snapshot,
                    )
                st.markdown(reply)

        st.session_state.messages.append(
            {"role": "assistant", "content": reply}
        )
        st.session_state.tool_log.append(tool_log)

        if tool_log:
            maybe_update_snapshot_from_log(tool_log, lat)

        st.rerun()


# =============================================================================
# Footer
# =============================================================================
st.markdown("---")
st.caption(
    "Built on pvlib-inspired sizing + NVIDIA NIM free tier + a 15-file "
    "Karpathy-style design wiki. Code: `stage1_5_wwtp_dc/design/`. "
    "Every number in chat traces back to either a tool output or a wiki entry — "
    "by design."
)
