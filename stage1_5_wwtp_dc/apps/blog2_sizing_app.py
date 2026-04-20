"""Blog 2 companion app — "Sizing a behind-the-meter inference site".

Lets a reader of Blog 2 pick an archetype (30/40/50/60 MGD WWTP) and see
the full sizing report update live: PV kWp, BESS MWh, DC IT MW, rack count,
tokens/s, grid impact, and annual revenue at four price points.

Stays deliberately separate from `stage1_5_wwtp_dc/app.py` (the Blog 1/3/4
dashboard) so each blog post has a single-purpose landing surface.

Run locally:
    streamlit run stage1_5_wwtp_dc/apps/blog2_sizing_app.py

Deploy:
    Streamlit Cloud entry point = stage1_5_wwtp_dc/apps/blog2_sizing_app.py
"""
from __future__ import annotations
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Make the stage1_5_wwtp_dc package importable when Streamlit runs this file
# directly (so `from stage1_5_wwtp_dc.design import ...` resolves).
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from stage1_5_wwtp_dc.design import (  # noqa: E402
    ARCHETYPES,
    PRICE_POINTS_USD_PER_MTOKEN,
    size_all,
    size_site,
)
from stage1_5_wwtp_dc.design.archetypes import ARCHETYPE_LABELS  # noqa: E402


# ---------------------------------------------------------------------------
# Page config + header
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="EnergyFlux — Blog 2: Sizing the Site",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("# Sizing a behind-the-meter inference site")
st.caption(
    "Companion to Blog 2. Pick a wastewater-plant size on the left and watch "
    "the PV, battery, data-center, and revenue numbers recompute from first "
    "principles. Every assumption is listed at the bottom."
)

# ---------------------------------------------------------------------------
# Sidebar — archetype picker
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Site archetype")
    picked = st.selectbox(
        "Pick a municipal WWTP size",
        options=list(ARCHETYPES.keys()),
        format_func=lambda k: ARCHETYPE_LABELS[k],
        index=0,
    )
    st.markdown(
        "AWWA utility benchmarking: ~70% of US WWTPs serving 50k–500k "
        "people fall into the 25–75 MGD band. These four archetypes cover "
        "that distribution."
    )

out = size_site(picked)

# ---------------------------------------------------------------------------
# Headline KPIs
# ---------------------------------------------------------------------------
st.markdown(f"## {out['label']}")

c1, c2, c3, c4 = st.columns(4)
c1.metric("☀️  PV nameplate", f"{out['pv']['kwp']:,.0f} kWp")
c2.metric("🔋  BESS capacity", f"{out['bess']['mwh']:.1f} MWh")
c3.metric("🖥️  DC IT load", f"{out['dc']['it_load_mw']:.2f} MW")
c4.metric("🧱  Racks (Blackwell NVL72)", f"{out['dc']['racks']:,}")

c5, c6, c7, c8 = st.columns(4)
c5.metric("💧  WWTP load", f"{out['site']['wwtp_load_kw']:,.0f} kW")
c6.metric("🔌  Peak added grid", f"{out['grid']['peak_added_kw']:,.0f} kW")
c7.metric("⚡  PV annual energy", f"{out['pv']['annual_mwh']:,.0f} MWh/yr")
c8.metric(
    "💬  Realized tokens/yr",
    f"{out['dc']['tokens_per_sec'] * 31_536_000 * out['dc']['utilization_factor'] / 1e12:.1f} T",
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Revenue at four price points
# ---------------------------------------------------------------------------
st.markdown("### Annual revenue — four price scenarios")

rev = out["revenue_per_year_usd"]
rev_df = pd.DataFrame(
    [
        {"price_per_mtoken_usd": p, "revenue_usd": rev[f"{p:.2f}_per_mtoken"]}
        for p in PRICE_POINTS_USD_PER_MTOKEN
    ]
)

col_chart, col_table = st.columns([2, 1])

with col_chart:
    fig = go.Figure(
        go.Bar(
            x=[f"${p:.2f}/M tok" for p in rev_df["price_per_mtoken_usd"]],
            y=rev_df["revenue_usd"],
            text=[f"${v / 1e6:,.1f} M" for v in rev_df["revenue_usd"]],
            textposition="outside",
            marker_color=["#EF5350", "#FFB300", "#42A5F5", "#4CAF50"],
        )
    )
    fig.update_layout(
        template="plotly_dark",
        height=380,
        yaxis_title="USD / year",
        yaxis=dict(tickformat="$,.0f"),
        margin=dict(t=20, b=40, l=60, r=20),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, key="rev_chart")

with col_table:
    rev_table = rev_df.copy()
    rev_table["price_per_mtoken_usd"] = rev_table["price_per_mtoken_usd"].map(
        lambda p: f"${p:.2f}"
    )
    rev_table["revenue_usd"] = rev_table["revenue_usd"].map(
        lambda v: f"${v / 1e6:,.1f} M"
    )
    rev_table.columns = ["Price / M tokens", "Revenue / year"]
    st.dataframe(rev_table, hide_index=True, use_container_width=True)

# ---------------------------------------------------------------------------
# Cross-archetype comparison table
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown("### All four archetypes side-by-side")

all_reports = size_all()
rows = []
for name, r in all_reports.items():
    rows.append(
        {
            "Archetype": ARCHETYPE_LABELS[name],
            "MGD": r["site"]["mgd"],
            "Buffer (ac)": r["site"]["buffer_acres"],
            "PV (kWp)": r["pv"]["kwp"],
            "BESS (MWh)": r["bess"]["mwh"],
            "DC IT (MW)": r["dc"]["it_load_mw"],
            "Racks": r["dc"]["racks"],
            "Tokens/s": r["dc"]["tokens_per_sec"],
            "Peak added (kW)": r["grid"]["peak_added_kw"],
            "Rev @ $0.10 ($M/yr)": round(r["revenue_per_year_usd"]["0.10_per_mtoken"] / 1e6, 1),
            "Rev @ $0.30 ($M/yr)": round(r["revenue_per_year_usd"]["0.30_per_mtoken"] / 1e6, 1),
        }
    )
comparison_df = pd.DataFrame(rows)
st.dataframe(comparison_df, hide_index=True, use_container_width=True)

# ---------------------------------------------------------------------------
# Revenue scaling curve (across all archetypes, all price points)
# ---------------------------------------------------------------------------
st.markdown("### How revenue scales with site size")

scaling_rows = []
for name, r in all_reports.items():
    for p in PRICE_POINTS_USD_PER_MTOKEN:
        scaling_rows.append(
            {
                "mgd": r["site"]["mgd"],
                "price": p,
                "revenue_musd": r["revenue_per_year_usd"][f"{p:.2f}_per_mtoken"] / 1e6,
            }
        )
scaling_df = pd.DataFrame(scaling_rows)

fig_scale = go.Figure()
palette = {0.05: "#EF5350", 0.10: "#FFB300", 0.20: "#42A5F5", 0.30: "#4CAF50"}
for price, sub in scaling_df.groupby("price"):
    sub = sub.sort_values("mgd")
    fig_scale.add_trace(
        go.Scatter(
            x=sub["mgd"],
            y=sub["revenue_musd"],
            mode="lines+markers",
            name=f"${price:.2f}/M tok",
            line=dict(width=3, color=palette[price]),
            marker=dict(size=10),
        )
    )
fig_scale.update_layout(
    template="plotly_dark",
    height=380,
    xaxis_title="Plant size (MGD)",
    yaxis_title="Annual revenue ($M)",
    legend=dict(orientation="h", y=1.08, x=0),
    margin=dict(t=30, b=40, l=60, r=20),
)
st.plotly_chart(fig_scale, use_container_width=True, key="scaling")

# ---------------------------------------------------------------------------
# Assumptions ledger — copy-pasteable into the blog
# ---------------------------------------------------------------------------
st.markdown("---")
with st.expander("📋  Show every assumption behind these numbers"):
    a = ARCHETYPES[picked]
    assumptions_rows = [
        ("WWTP electrical load", f"{a['wwtp_kw_per_mgd']:.1f} kW per MGD",
         "Derived from BSM1-calibrated sim at 30 MGD (stage1_5)."),
        ("Biogas CHP offset", f"{a['biogas_offset_kw']:.0f} kW constant",
         "Typical for ≥25 MGD plants with anaerobic digestion."),
        ("PV array density", f"{a['pv_density_kwp_per_acre']:.0f} kWp/acre",
         "Ground-mount single-axis tracker, fixed tilt."),
        ("PV land fraction", f"{a['pv_land_fraction']*100:.0f}% of buffer",
         "Reserved 10% for access roads + inverter pads."),
        ("PV capacity factor", f"{a['pv_capacity_factor']*100:.1f}%",
         "Southwest US 2024 PVlib actuals."),
        ("BESS duration", f"{a['bess_duration_hours']:.1f} hours",
         "Industry-standard 4-hour lithium-ion."),
        ("DC IT share of PV", f"{a['dc_it_share_of_pv_dc']*100:.0f}%",
         "Sized so PV + BESS can serve DC through the evening peak."),
        ("Facility PUE", f"{a['pue']:.2f}",
         "Modern liquid-cooled facility (rear-door heat exchanger + free cooling)."),
        ("Per-rack facility draw", f"{a['rack_facility_kw']:.0f} kW",
         "Blackwell GB200 NVL72 at nameplate facility power."),
        ("Tokens/s per MW", f"{a['tokens_per_sec_per_mw']:.2e}",
         "Blackwell tensor cores at FP8 on mid-size LLMs."),
        ("DC time-averaged utilization", f"{out['dc']['utilization_factor']*100:.0f}%",
         "Steady-state inference serving; queue rarely empties."),
    ]
    df_asm = pd.DataFrame(
        assumptions_rows,
        columns=["Parameter", "Value", "Basis"],
    )
    st.dataframe(df_asm, hide_index=True, use_container_width=True)

st.caption(
    "Source: `stage1_5_wwtp_dc/design/archetypes.py` + `sizing.py`. "
    "See GitHub for the full repo and Blog 1 for the motivation behind "
    "wastewater-plant buffer zones as inference hosts."
)
