"""Blog 2 demo — vault-backed AI assistant.

Successor to ``blog2_genai_app.py``. Three changes vs the legacy app:

1. **Retrieves from the EnergyFlux Knowledge Vault** (via
   ``design.rag_v2``), not the stage-local ``design_wiki/``.
2. **Authority is visible.** Every retrieved hit is rendered with
   an authority badge; primary citations (Authoritative + Reviewed)
   are highlighted; Candidate / Legacy citations show a "pending
   review" warning.
3. **Wiki link is a first-class affordance.** Each hit links to its
   page on the published wiki; the top status bar links to the wiki
   home; the footer notes the cloud-vs-private deployment story.

Run locally:
    streamlit run stage1_5_wwtp_dc/apps/blog2_genai_app_v2.py

Streamlit Cloud entry point (set this in app config):
    stage1_5_wwtp_dc/apps/blog2_genai_app_v2.py

Secrets:
    NVIDIA_API_KEY        — required for live LLM mode (free at build.nvidia.com)
    EF_WIKI_URL_BASE      — optional override for the wiki URL prefix
                             (default: "wiki" → links resolve to wiki/...)
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(REPO_ROOT / ".env")
except ImportError:
    pass

from stage1_5_wwtp_dc.design.pv_tools import (  # noqa: E402
    array_layout, calc_annual_yield, design_pv_array, MODULE_CATALOG,
)
from stage1_5_wwtp_dc.design.rag_v2 import VaultRetriever  # noqa: E402
from stage1_5_wwtp_dc.design.sizing import size_site  # noqa: E402
from stage1_5_wwtp_dc.design.archetypes import ARCHETYPES, ARCHETYPE_LABELS  # noqa: E402


# =============================================================================
# Vault wiring
# =============================================================================
WIKI_URL_BASE = os.getenv("EF_WIKI_URL_BASE", "wiki").rstrip("/")


@st.cache_resource(show_spinner=False)
def _get_retriever() -> VaultRetriever:
    return VaultRetriever(wiki_url_base=WIKI_URL_BASE)


def _wiki_url(path_or_segment: str) -> str:
    """Convert a raw vault relative path (or already-prefixed wiki url) to a
    URL we can hand to a browser. Honors EF_WIKI_PUBLIC_BASE if set so that
    the Streamlit app deployed on a different domain can still link back to
    the published wiki."""
    public_base = os.getenv("EF_WIKI_PUBLIC_BASE", "").rstrip("/")
    if public_base:
        # path_or_segment may already be "wiki/foo.html"; strip the local
        # base and re-prefix with the public one.
        rel = path_or_segment
        if rel.startswith(WIKI_URL_BASE + "/"):
            rel = rel[len(WIKI_URL_BASE) + 1:]
        return f"{public_base}/{rel}"
    return path_or_segment


AUTHORITY_COLORS = {
    "authoritative": "#1F4E79",
    "reviewed":      "#2F855A",
    "candidate":     "#E8A33D",
    "legacy":        "#888888",
}
PRIMARY_AUTHORITIES = {"authoritative", "reviewed"}


def _badge(authority: str) -> str:
    color = AUTHORITY_COLORS.get(authority, "#666")
    return (
        f'<span style="display:inline-block; padding:1px 8px; border-radius:10px; '
        f'background:{color}; color:white; font-size:11px; font-weight:600; '
        f'margin-right:6px; vertical-align:middle;">{authority.upper()}</span>'
    )


# =============================================================================
# Helpers
# =============================================================================
def render_tool_result(entry: dict) -> None:
    tool = entry["tool"]
    result = entry["result"]
    if tool == "retrieve":
        hits = (result or {}).get("hits", [])
        if not hits:
            st.caption("No vault hits.")
            return
        for h in hits:
            authority = h.get("authority", "candidate")
            wiki_url = _wiki_url(h.get("wiki_url", ""))
            is_primary = authority in PRIMARY_AUTHORITIES
            # First line: badge + title + score + wiki link
            st.markdown(
                f"{_badge(authority)} **{h['title']}** &nbsp;"
                f'<span style="color:#666; font-size:12px;">score {h["score"]:.2f}</span>'
                + (f' &nbsp;·&nbsp; <a href="{wiki_url}" target="_blank">View on wiki →</a>' if wiki_url else "")
                + ("" if is_primary else
                   ' &nbsp;<span style="color:#B91C1C; font-size:11px;">⚠ pending review</span>'),
                unsafe_allow_html=True,
            )
            st.caption(h.get("excerpt", "")[:300])
    else:
        st.json(result, expanded=False)


def run_live(user_prompt: str, api_key: str, model_name: str,
             prior_messages: list) -> tuple[str, list]:
    try:
        from stage1_5_wwtp_dc.design.llm_v2 import (
            SYSTEM_PROMPT, make_client, run_tool_loop,
        )
    except Exception as e:  # noqa: BLE001
        return (f"❌ LLM import failed: {e}", [])

    try:
        client, mdl = make_client(api_key=api_key, model=model_name)
    except RuntimeError as e:
        return f"❌ {e}", []

    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in prior_messages:
        history.append({"role": m["role"], "content": m["content"]})
    history.append({"role": "user", "content": user_prompt})

    try:
        _updated, final_text, tool_log = run_tool_loop(
            client=client, model=mdl, messages=history, max_steps=6,
        )
    except Exception as e:  # noqa: BLE001
        return (f"❌ NIM call failed: `{e}`. Check API key or rate limits.", [])

    return final_text, tool_log


def run_mock(user_prompt: str, snapshot: dict, retriever: VaultRetriever) -> tuple[str, list]:
    """No-LLM fallback: do a direct vault retrieval and summarize."""
    hits = retriever.retrieve(user_prompt, k=3)
    d = snapshot["design"]
    y = snapshot["yield"]
    bullets = []
    for h in hits:
        wiki_url = _wiki_url(h["wiki_url"])
        bullets.append(
            f"- **{h['title']}** *(authority: {h['authority']})* — "
            f"[{wiki_url}]({wiki_url})"
        )
    bullets_text = "\n".join(bullets) if bullets else "_(vault returned no hits)_"
    reply = (
        f"_(mock mode — no NVIDIA NIM key detected. The vault retrieval ran; "
        f"the LLM summarization step did not.)_\n\n"
        f"**Your question:** {user_prompt}\n\n"
        f"**Top vault matches:**\n{bullets_text}\n\n"
        f"**Sidebar snapshot for context:**\n"
        f"- PV nameplate: {d['kwp_dc']:,.0f} kWp DC ({d['module_count']:,} × {d['module_w']} W)\n"
        f"- Annual yield: {y['annual_mwh']:,.0f} MWh at {y['capacity_factor_pct']:.1f}% CF\n\n"
        f"Add an NVIDIA NIM key in the sidebar to run the assistant for real."
    )
    fake_log = [{"tool": "retrieve", "args": {"query": user_prompt, "k": 3},
                 "result": {"hits": hits, "query": user_prompt, "k": 3,
                            "backend": retriever.backend}}]
    return reply, fake_log


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
    page_title="EnergyFlux — Vault-backed AI Assistant",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Status bar at the very top — shows vault stats and links to the wiki.
retriever = _get_retriever()
stats = retriever.stats()
wiki_home_url = _wiki_url(f"{WIKI_URL_BASE}/index.html")

st.markdown(
    f"""<div style="background:#F4F7FB; border:1px solid #9DC3E6; padding:8px 14px;
                    margin-bottom:14px; font-size:13.5px; border-radius:2px;">
    <strong style="color:#1F4E79;">Backed by the EnergyFlux Knowledge Vault</strong>
    &nbsp;·&nbsp;
    {_badge('authoritative')}{stats.get('authoritative', 0)}
    {_badge('reviewed')}{stats.get('reviewed', 0)}
    {_badge('candidate')}{stats.get('candidate', 0)}
    {_badge('legacy')}{stats.get('legacy', 0)}
    &nbsp;·&nbsp;
    <a href="{wiki_home_url}" target="_blank">browse the wiki →</a>
    </div>""",
    unsafe_allow_html=True,
)

st.markdown("# Vault-backed AI assistant for industrial AI siting")
st.caption(
    "Ask questions, get answers grounded in a governed engineering knowledge "
    "base. Each citation is tagged with its authority level — only "
    "authoritative and reviewed pages are cited as fact; candidate and legacy "
    "pages show up only when nothing more reliable exists, and always with a "
    "'pending review' tag. The same retrieval back-end runs on public cloud "
    "(this demo) or behind a corporate firewall — see the footer for "
    "deployment notes."
)


# =============================================================================
# Sidebar
# =============================================================================
with st.sidebar:
    st.markdown("### Site inputs")
    area_acres = st.slider("Available buffer area (acres)", 5, 60, 23, step=1)
    lat = st.slider("Site latitude (°N)", 24.0, 49.0, 30.27, step=0.1)
    module_w = st.selectbox("Module wattage", sorted(MODULE_CATALOG.keys()),
                            index=sorted(MODULE_CATALOG.keys()).index(580))
    tracking = st.selectbox(
        "Tracking", ["single_axis", "fixed_tilt", "dual_axis"], index=0,
    )
    bifacial = st.checkbox("Bifacial modules", value=True)

    st.markdown("---")
    st.markdown("### NVIDIA NIM")
    api_key_input = st.text_input(
        "API key (free at build.nvidia.com)",
        value=os.getenv("NVIDIA_API_KEY", os.getenv("NVIDIA_NIM_API_KEY", "")),
        type="password",
    )
    model = st.selectbox(
        "Model",
        [
            "meta/llama-3.1-70b-instruct",
            "meta/llama-3.1-405b-instruct",
            "openai/gpt-oss-120b",
            "deepseek-ai/deepseek-v3",
        ],
        index=0,
    )
    live_mode = bool(api_key_input.strip())
    st.caption(f"Mode: **{'🟢 live' if live_mode else '🟠 mock (vault-only)'}**")

    st.markdown("---")
    st.markdown("### About this vault")
    st.caption(
        f"{stats.get('total', 0)} pages currently indexed. "
        f"None at *authoritative* or *reviewed* yet — the vault is in early "
        f"build-out, and most content is *candidate* awaiting senior-engineer "
        f"approval. Check back as the EnergyFlux blog series progresses; "
        f"each new post promotes vault content."
    )


# =============================================================================
# Session state
# =============================================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "tool_log" not in st.session_state:
    st.session_state.tool_log = []
if "design_snapshot" not in st.session_state:
    st.session_state.design_snapshot = None

st.session_state.design_snapshot = snapshot_from_args(
    area_acres, lat, module_w, tracking, bifacial,
)


# =============================================================================
# Two-column main area
# =============================================================================
col_chat, col_cards = st.columns([3, 2], gap="large")


# ---- RIGHT: live cards + viz ----
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
        f"Tracking: `{design['tracking']}`  •  "
        f"Module: {design['module_w']} W ({MODULE_CATALOG[design['module_w']]['technology']})  •  "
        f"Zone: `{yld['zone']}`  •  PR: {yld['performance_ratio']:.2f}"
    )

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

    st.markdown("---")
    with st.expander("📐 Archetype-matched full site sizing"):
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


# ---- LEFT: chat ----
with col_chat:
    st.markdown("### Conversation")

    # Suggested-question buttons. These exercise the vault's content
    # at different authority levels and across different sections.
    if not st.session_state.messages:
        with st.container(border=True):
            st.markdown("**Try one of these to get started:**")
            sa, sb, sc, sd = st.columns(4)
            buttons = [
                (sa, "WWTP siting case",
                 "Why are mid-size municipal WWTPs the case study for "
                 "behind-the-meter AI inference siting? What three "
                 "resources need to be on-site?"),
                (sb, "Why 4-hour BESS",
                 "Why is the 4-hour LFP BESS the industry default? Walk me "
                 "through the capacity-credit + TOU + fire-code reasons."),
                (sc, "21 racks, why",
                 "How does the 45 MGD WWTP archetype land on 21 racks of "
                 "GB200, and why does the 4 MVA transformer need an upgrade?"),
                (sd, "BTM hosts compared",
                 "Compare WWTP, chemical sites, distribution substations, "
                 "and large institutional campuses as BTM AI hosts."),
            ]
            for col, label, q in buttons:
                if col.button(label, use_container_width=True):
                    st.session_state.prefill = q
                    st.rerun()

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

    prefill = st.session_state.pop("prefill", "")
    prompt = st.chat_input("Ask the vault-backed assistant…") or prefill or ""

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Retrieving from vault and composing…"):
                if live_mode:
                    reply, tool_log = run_live(
                        prompt, api_key_input, model,
                        prior_messages=st.session_state.messages[:-1],
                    )
                else:
                    reply, tool_log = run_mock(
                        prompt, st.session_state.design_snapshot, retriever,
                    )
                st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.session_state.tool_log.append(tool_log)

        if tool_log:
            maybe_update_snapshot_from_log(tool_log, lat)

        st.rerun()


# =============================================================================
# Footer — deployment note
# =============================================================================
st.markdown("---")
st.markdown(
    """<div style="font-size:13px; color:#666; line-height:1.6;">
<strong style="color:#1F4E79;">Architecture note.</strong>
This public demo runs on Streamlit Community Cloud and calls a hosted LLM
(NVIDIA NIM free tier). The same code path runs unchanged behind a
corporate firewall: replace the public Git repo with GitLab Enterprise or
GitHub Enterprise, replace Streamlit Community Cloud with an internal
deployment, and replace the hosted LLM with on-prem Llama, Qwen, or
DeepSeek via Ollama or vLLM. The vault, the retriever, the authority
discipline, and the approval workflow stay the same. The point of the
governance hierarchy isn't the hosting choice — it's that the AI
assistant cites only signed-off content, and that the audit trail
follows every approval. See
<a href="{wiki_home_url}" target="_blank" style="color:#1F4E79;">the wiki's
governance page</a> for how promotion from candidate to reviewed works.
</div>""".format(wiki_home_url=wiki_home_url),
    unsafe_allow_html=True,
)
