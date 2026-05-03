"""Blog 2 flowsheet app — main entry point.

Layout v4: **copilot lives in the sidebar**, always visible, scrolls
independently from the main design area. This matches the user's request
("split-screen: chat on one side, design on the other, ask while looking").
Streamlit's sidebar is the one native split-screen pattern it has; we lean
on it.

    ┌──────────┬──────────────────────────────────────────────────────┐
    │          │  Title + action buttons                               │
    │          │  ── KPI strip ──                                      │
    │ SIDEBAR  ├─────────────────────────────┬────────────────────────┤
    │          │                             │                        │
    │ 🤖       │       FLOWSHEET             │    EDITING: <block>    │
    │ Copilot  │       CANVAS                │    [sliders/selects]   │
    │ (always  │                             │    [output KPIs]       │
    │  visible │                             │                        │
    │  scrolls │       [block picker]        │                        │
    │  indep)  │                             │                        │
    │          │                             │                        │
    └──────────┴─────────────────────────────┴────────────────────────┘

Why this is better than v3 (editor+copilot stacked in right col):
* Copilot visible at all times, NO scrolling needed to find it
* User can ask a question while looking at the block editor at full size
* Sidebar scrolls independently, so long chat history doesn't push the
  design off screen
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Load .env for NVIDIA_API_KEY auto-pickup
try:
    from dotenv import load_dotenv
    load_dotenv(REPO_ROOT / ".env")
except ImportError:
    pass

from stage1_5_wwtp_dc.design.archetypes import PRICE_POINTS_USD_PER_MTOKEN  # noqa: E402
from stage1_5_wwtp_dc.apps.flowsheet.blocks import (  # noqa: E402
    default_design,
    recompute_all,
)
from stage1_5_wwtp_dc.apps.flowsheet.canvas import render_flowsheet  # noqa: E402
from stage1_5_wwtp_dc.apps.flowsheet.editors import render_editor  # noqa: E402
from stage1_5_wwtp_dc.apps.flowsheet.copilot import (  # noqa: E402
    render_copilot_panel,
)
from stage1_5_wwtp_dc.apps.flowsheet.report import render_report  # noqa: E402


# ---------------------------------------------------------------------------
# Page config — SIDEBAR EXPANDED so copilot is visible on load
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="EnergyFlux — AI Factory Flowsheet Designer",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS — wider sidebar (copilot needs room), tighter spacing
st.markdown("""
<style>
/* Sidebar: wide enough for readable chat */
section[data-testid="stSidebar"] {
    min-width: 440px !important;
    max-width: 520px !important;
    background-color: #0E1117 !important;
    border-right: 2px solid rgba(255,209,102,0.25);
}
section[data-testid="stSidebar"] > div:first-child {
    padding-top: 0.8rem;
}
/* Sidebar chat input — make it stand out */
section[data-testid="stSidebar"] div[data-testid="stChatInput"] {
    background: rgba(255,209,102,0.05) !important;
    border: 1.5px solid rgba(255,209,102,0.4) !important;
    border-radius: 8px;
}
/* Main area */
.block-container {padding-top: 0.6rem; padding-bottom: 0.6rem; max-width: none;}
h1 {font-size: 1.35rem !important; margin-bottom: 0.15rem !important;}
h3 {font-size: 1.08rem !important; margin-top: 0 !important;}
h4 {font-size: 0.95rem !important; margin-top: 0.3rem !important; margin-bottom: 0.3rem !important;}
div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.04);
    padding: 6px 10px;
    border-radius: 6px;
}
div[data-testid="stMetricValue"] {font-size: 1.20rem !important;}
div[data-testid="stMetricLabel"] {font-size: 0.76rem !important;}
/* Compact top-right buttons — icon-only */
div.stButton > button {
    white-space: nowrap;
    font-size: 0.85rem;
    padding: 0.3rem 0.6rem;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "design" not in st.session_state:
    st.session_state.design = recompute_all(default_design())

if "selected_block" not in st.session_state:
    st.session_state.selected_block = "pv"


# ===========================================================================
#                               SIDEBAR — COPILOT
# ===========================================================================
with st.sidebar:
    # ── Action buttons ─
    st.markdown("### ⚙️ Actions")
    sb_act = st.columns(2)
    if sb_act[0].button("📋 Report", use_container_width=True,
                        help="One-page professional site design report"):
        st.session_state["_show_report"] = not st.session_state.get("_show_report", False)
    if sb_act[1].button("📖 Defaults", use_container_width=True,
                        help="Show where each default parameter came from"):
        st.session_state["_show_defaults"] = not st.session_state.get("_show_defaults", False)

    sb_act2 = st.columns(2)
    if sb_act2[0].button("🔄 Reset", use_container_width=True,
                         help="Reset to default Austin 23-ac design"):
        st.session_state.design = recompute_all(default_design())
        st.session_state.selected_block = "pv"
        st.rerun()
    if sb_act2[1].button("📥 JSON", use_container_width=True,
                         help="Show the raw design as JSON"):
        import json
        st.session_state["_export"] = json.dumps(
            {k: {"params": v["params"], "outputs": v["outputs"]}
             for k, v in st.session_state.design.items()},
            indent=2, default=str,
        )
    st.markdown("---")

    # ── Copilot ─
    st.markdown("### 🤖 Design Copilot")
    st.markdown(
        f"<div style='color:#9AA6B2; font-size:0.82rem;'>"
        f"Currently editing: "
        f"<span style='color:#FFD166'>"
        f"{st.session_state.design[st.session_state.selected_block]['label']}"
        f"</span></div>",
        unsafe_allow_html=True,
    )

    api_key = (os.getenv("NVIDIA_API_KEY")
               or os.getenv("NVIDIA_NIM_API_KEY") or "")

    # Model picker — stronger free-tier models available
    model_options = {
        "meta/llama-3.1-70b-instruct":       "Llama 3.1 70B  — fast, balanced",
        "meta/llama-3.1-405b-instruct":      "Llama 3.1 405B — strongest, slower",
        "deepseek-ai/deepseek-v3":           "DeepSeek V3    — strong reasoning",
        "openai/gpt-oss-120b":               "GPT-OSS 120B   — Nemotron replacement",
        "qwen/qwen2.5-72b-instruct":         "Qwen 2.5 72B   — strong multilingual",
    }
    model = st.selectbox(
        "LLM model (NVIDIA NIM free tier)",
        options=list(model_options.keys()),
        format_func=lambda k: model_options[k],
        index=1,  # default to 405B for smarter copilot behavior
        help="Larger = smarter but slower + more credits. 405B and DeepSeek "
             "V3 follow the system prompt much better than 70B.",
        key="copilot_model_picker",
    )
    render_copilot_panel(
        design=st.session_state.design,
        selected_block=st.session_state.selected_block,
        api_key=api_key,
        model=model,
        key_prefix="sidebar_copilot",
    )


# ===========================================================================
#                               MAIN AREA
# ===========================================================================

# Row 1 — Title only. All action buttons moved to the sidebar (which is
# always visible) so they can never get clipped by narrow Chrome windows.
st.markdown(
    "### ⚡ AI Factory Flowsheet Designer "
    "<span style='color:#9AA6B2; font-size:0.82rem'>"
    "· block-based · live-recompute · actions &amp; copilot ← in sidebar</span>",
    unsafe_allow_html=True,
)

# Hint about tooltips — Aspen F1 equivalent
st.caption(
    "💡 Hover the **ⓘ** icon next to any parameter to see its meaning "
    "and source. Or ask the copilot on the left."
)

# Report view — renders inline above the workspace when active
if st.session_state.get("_show_report"):
    st.markdown("---")
    with st.container(border=True):
        render_report(st.session_state.design)
    st.markdown("---")

# Popovers (Defaults table / JSON export)
if st.session_state.get("_show_defaults"):
    with st.expander("📖 Where do these default values come from?", expanded=True):
        st.markdown("""
| Parameter | Default | Source |
|---|---|---|
| `area_acres` | 23 | Typical 90% of buffer-zone usable land at 45 MGD WWTP. `design_wiki/regulations/wwtp_buffer_setback.md`. |
| `lat` | 30.27°N | Austin-Bergstrom airport — Blog 2 running example. |
| `module_w` | 580 W | TOPCon bifacial, utility-scale workhorse 2025-26. `design_wiki/pv/bifacial_gain.md`. |
| `tracking` | single-axis + bifacial | Industry default, +25% over fixed mono. `design_wiki/pv/single_axis_tracker.md`. |
| `gcr` | 0.35 | Single-axis tracker standard. Pitch = 2.4m/0.35 ≈ 6.9m. |
| `modules_per_tracker` | 90 | Typical 2×45, 1500V string. |
| `performance_ratio` | 0.82 | PVWatts default after all derates. |
| `inverter kW` | 550 | Common utility central inverter. |
| `ILR` | 1.25 | DC/AC ratio industry standard 1.2-1.3. |
| `mgd` | 45 | Upper-middle of 25-75 MGD "volume sweet spot". |
| `kw_per_mgd` | 83.33 | From stage1 BSM1 sim at 30 MGD = 2500 kW. |
| `biogas_offset_kw` | 800 | Typical CHP for ≥25 MGD plants. |
| `hardware_key` | blackwell_gb200 | Currently shipping Q3 2025+. `design_wiki/hardware/blackwell_gb200_nvl72.md`. |
| `utilization` | 0.70 | Steady-state inference serving. |
| `bess duration` | 4 h | `design_wiki/bess/4h_battery_standard.md`. |
| `chg/disch ratio` | 0.5 | stage1 dispatch default. |
| `service_voltage_kv` | 25.0 | Common US MV service for 5-25 MW. |
| `existing_xfmr_mva` | 4.0 | Typical WWTP service transformer at 30-50 MGD. |

Every default is **editable** in the block's parameter panel on the right.
        """)

if st.session_state.get("_export"):
    with st.expander("📋 Exported design JSON", expanded=True):
        st.code(st.session_state._export, language="json")
        if st.button("Close export", key="close_export"):
            st.session_state.pop("_export")
            st.rerun()


# Row 2 — KPI strip (horizontal)
d = st.session_state.design
pv_o = d["pv"]["outputs"]
rack_o = d["rack"]["outputs"]
dc_o = d["dc"]["outputs"]
bess_o = d["bess"]["outputs"]
grid_o = d["grid"]["outputs"]

kpi_cols = st.columns(6)
kpi_cols[0].metric("PV nameplate", f"{pv_o.get('kwp_dc', 0):,.0f} kWp")
kpi_cols[1].metric("DC IT load", f"{rack_o.get('it_mw', 0):.2f} MW")
kpi_cols[2].metric("BESS", f"{bess_o.get('mwh', 0):.1f} MWh")
kpi_cols[3].metric("Annual energy", f"{pv_o.get('annual_mwh', 0):,.0f} MWh")
kpi_cols[4].metric(
    "Peak added",
    f"{grid_o.get('peak_added_kw', 0):,.0f} kW",
    delta="xfmr upgrade" if grid_o.get('upgrade_required') else "within headroom",
    delta_color="inverse" if grid_o.get('upgrade_required') else "normal",
)
rev = dc_o.get("revenue_per_year_usd", {}).get("0.10", 0)
kpi_cols[5].metric("Revenue @ $0.10/Mtok", f"${rev/1e6:.1f} M/yr")

st.markdown("<hr style='margin: 0.6rem 0 0.6rem 0; opacity: 0.25'>",
            unsafe_allow_html=True)


# Row 3 — Flowsheet (left wide) + Editor (right)
col_canvas, col_edit = st.columns([1.4, 1.0], gap="small")

with col_canvas:
    st.markdown("#### Flowsheet")
    clicked = render_flowsheet(
        design=st.session_state.design,
        selected_block=st.session_state.selected_block,
        key="main_canvas",
        height=600,
    )
    if clicked and clicked != st.session_state.selected_block:
        st.session_state.selected_block = clicked
        st.rerun()

    st.caption("Or switch block directly:")
    bpick = st.columns(7)
    labels = {
        "pv": "☀️ PV", "inv": "🔌 Inv", "bess": "🔋 BESS",
        "dc": "⚡ DC", "rack": "🖥️ Rack", "wwtp": "💧 WWTP", "grid": "🧱 Grid",
    }
    for col, (bid, lbl) in zip(bpick, labels.items()):
        if col.button(
            lbl, use_container_width=True,
            type="primary" if bid == st.session_state.selected_block else "secondary",
            key=f"pick_{bid}",
        ):
            st.session_state.selected_block = bid
            st.rerun()

with col_edit:
    st.markdown(
        f"#### Editing: "
        f"<span style='color:#FFD166'>{d[st.session_state.selected_block]['label']}</span>",
        unsafe_allow_html=True,
    )
    changed = render_editor(st.session_state.selected_block, st.session_state.design)
    if changed:
        st.session_state.design = recompute_all(st.session_state.design)
        st.rerun()


# ────────────────────────────────────────────────────────────────────────
# Knowledge-graph section (added v4.1 — hand-curated, manifest-driven)
# Shows the structured relationship between flowsheet blocks and the wiki
# entries the copilot retrieves from. The PNG is regenerated by
# `scripts/build_blog2_fig8_wiki_graph.py`. The single source of truth for
# nodes and edges is `scripts/wiki_graph_manifest.py`.
# ────────────────────────────────────────────────────────────────────────
st.markdown("<hr style='margin: 0.6rem 0 0.3rem 0; opacity: 0.2'>",
            unsafe_allow_html=True)
st.markdown("#### 📊 Design wiki — knowledge graph view")
st.caption(
    "A hand-curated view of the design wiki used by the copilot. The graph "
    "shows how source notes attach to sizing assumptions and how those "
    "assumptions propagate through the flowsheet. It is not an automated "
    "proof of buildability; it is a traceability layer for engineering review."
)
graph_png = REPO_ROOT / "blog" / "_sources" / "blog2_fig8_wiki_graph.png"
if graph_png.exists():
    st.image(str(graph_png), use_container_width=True)
else:
    st.info(
        "Knowledge-graph image not found. Run "
        "`python scripts/build_blog2_fig8_wiki_graph.py` to generate it."
    )

# Footer
st.markdown("<hr style='margin: 0.6rem 0 0.3rem 0; opacity: 0.2'>",
            unsafe_allow_html=True)
cap_cols = st.columns(3)
cap_cols[0].caption(
    "**Under the hood:** blocks recompute from `stage1_5_wwtp_dc/design/`. "
    "Nothing invented."
)
cap_cols[1].caption(
    "**Paradigm:** Aspen / ETAP / SAM-style flowsheet. "
    "Engineer drives; copilot assists from the sidebar."
)
cap_cols[2].caption(
    "**Source:** `apps/flowsheet/{blocks,canvas,editors,copilot}.py` &nbsp;·&nbsp; "
    "graph: `scripts/wiki_graph_manifest.py`"
)
