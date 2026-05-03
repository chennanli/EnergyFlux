"""Plotly flowsheet canvas — renders the 7 blocks with arrows and click-to-select.

Uses ``st.plotly_chart(on_select="rerun", selection_mode="points")`` to detect
block clicks. When the user clicks a block rectangle, Streamlit reruns and we
route ``clicked_block_id`` into ``st.session_state.selected_block``.

Design rationale
----------------
* **Plotly, not streamlit-flow.** React Flow wrappers for Streamlit are
  third-party and version-flaky. Plotly is core Streamlit, reliably works in
  1.56+, and gives us pixel-perfect control over rectangle rendering.
* **No drag-drop (yet).** Block positions are fixed in ``BLOCK_LAYOUT``.
  The click→select→edit→recompute loop is what actually feels like Aspen;
  drag-drop can come later without breaking anything built tonight.
* **Edge labels show live power flow** in kW or MW. These update every
  recompute so the engineer can eyeball whether, e.g., PV AC output equals
  DC bus inflow (they should, within inverter efficiency).

Streamlit selection-event contract
----------------------------------
st.plotly_chart returns an event dict like::

    {"selection": {"points": [{"customdata": "pv", ...}, ...]}}

We tag each block's center scatter marker with ``customdata=block_id`` so the
picked point's customdata tells us which block was clicked.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import plotly.graph_objects as go
import streamlit as st

from .blocks import (
    BLOCK_COLORS,
    BLOCK_LAYOUT,
    BLOCK_SELECTED_BORDER,
    BLOCK_NORMAL_BORDER,
    BLOCK_TEXT_ON,
    FLOWSHEET_EDGES,
    edge_flow_kw,
    headline_metric,
)


# Canvas extents (abstract units; same as BLOCK_LAYOUT coordinates).
CANVAS_W = 12.5
CANVAS_H = 10.0


def render_flowsheet(
    design: Dict[str, Dict[str, Any]],
    selected_block: Optional[str] = None,
    key: str = "flowsheet_canvas",
    height: int = 560,
) -> Optional[str]:
    """Render the flowsheet. Returns the block_id the user just clicked
    (or None if no new click on this rerun).
    """
    fig = go.Figure()

    # ── 1. Edges (drawn first so they sit under blocks) ─────────────────────
    for src, dst, unit_label in FLOWSHEET_EDGES:
        _draw_edge(fig, design, src, dst, unit_label)

    # ── 2. Blocks (rectangles + label + headline metric) ────────────────────
    for block_id, layout in BLOCK_LAYOUT.items():
        if block_id not in design:
            continue
        block = design[block_id]
        _draw_block(fig, block_id, block, layout, selected=(block_id == selected_block))

    # ── 3. Invisible click-targets (one big scatter point per block) ────────
    _draw_click_targets(fig, design)

    # ── 4. Layout polish ────────────────────────────────────────────────────
    fig.update_xaxes(range=[0, CANVAS_W], visible=False, fixedrange=True)
    # Reversed y-axis (top-origin). Do NOT set scaleanchor — lets the canvas
    # fill the container width at any Chrome zoom level without shrinking to
    # a small square.
    fig.update_yaxes(range=[CANVAS_H, 0], visible=False, fixedrange=True)
    fig.update_layout(
        template="plotly_dark",
        height=height,
        autosize=True,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        plot_bgcolor="#0F1116",
        paper_bgcolor="#0F1116",
        hovermode="closest",
        dragmode=False,
    )

    # ── 5. Dispatch click event back to caller ──────────────────────────────
    event = st.plotly_chart(
        fig,
        key=key,
        on_select="rerun",
        selection_mode=("points",),
        use_container_width=True,
        config={"displayModeBar": False, "staticPlot": False},
    )

    clicked = _extract_clicked_block_id(event)
    return clicked


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------
def _draw_block(
    fig: go.Figure,
    block_id: str,
    block: Dict[str, Any],
    layout: Dict[str, float],
    selected: bool,
) -> None:
    x, y, w, h = layout["x"], layout["y"], layout["w"], layout["h"]

    border = BLOCK_SELECTED_BORDER if selected else BLOCK_NORMAL_BORDER
    border_w = 4 if selected else 1.8

    # Filled rectangle
    fig.add_shape(
        type="rect",
        x0=x, y0=y, x1=x + w, y1=y + h,
        line=dict(color=border, width=border_w),
        fillcolor=BLOCK_COLORS[block["kind"]],
        opacity=0.95,
        layer="below",
    )

    # Block title
    fig.add_annotation(
        x=x + w / 2, y=y + 0.32,
        text=f"<b>{block['label']}</b>",
        showarrow=False,
        font=dict(size=13, color=BLOCK_TEXT_ON),
    )

    # Headline metric (live output)
    metric = headline_metric(block)
    if metric:
        fig.add_annotation(
            x=x + w / 2, y=y + 0.75,
            text=metric,
            showarrow=False,
            font=dict(size=11, color="rgba(255,255,255,0.88)"),
        )

    # Small "edit" hint
    fig.add_annotation(
        x=x + w - 0.08, y=y + h - 0.13,
        text="⚙",
        showarrow=False,
        font=dict(size=13, color="rgba(255,255,255,0.55)"),
        xanchor="right", yanchor="bottom",
    )


def _draw_edge(
    fig: go.Figure,
    design: Dict[str, Dict[str, Any]],
    src: str,
    dst: str,
    unit_label: str,
) -> None:
    src_layout = BLOCK_LAYOUT[src]
    dst_layout = BLOCK_LAYOUT[dst]

    # Pick exit/entry points based on relative position — right side if dst
    # is to the right, bottom side if dst is below, etc.
    sx, sy = _exit_point(src_layout, dst_layout)
    dx, dy = _entry_point(dst_layout, src_layout)

    # Arrow line via an annotation (Plotly arrow).
    fig.add_annotation(
        x=dx, y=dy, ax=sx, ay=sy,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True,
        arrowhead=2, arrowsize=1.2, arrowwidth=2.2,
        arrowcolor="rgba(180,190,210,0.7)",
        text="",
    )

    # Power-flow label at the midpoint, slightly offset.
    flow_kw = edge_flow_kw(design, src, dst)
    label = _format_flow(flow_kw, unit_label)
    mx = (sx + dx) / 2
    my = (sy + dy) / 2
    fig.add_annotation(
        x=mx, y=my - 0.12,
        text=f"<span style='color:#FFD166'>{label}</span>",
        showarrow=False,
        font=dict(size=10),
        bgcolor="rgba(15,17,22,0.85)",
        borderpad=3,
    )


def _draw_click_targets(fig: go.Figure, design: Dict[str, Dict[str, Any]]) -> None:
    """One scatter point at each block's center carrying block_id as customdata.
    Plotly's selection event returns the customdata of the point clicked; we
    recover the block_id from there."""
    xs, ys, ids, labels = [], [], [], []
    for bid, lay in BLOCK_LAYOUT.items():
        xs.append(lay["x"] + lay["w"] / 2)
        ys.append(lay["y"] + lay["h"] / 2)
        ids.append(bid)
        labels.append(design[bid]["label"])

    fig.add_trace(go.Scatter(
        x=xs, y=ys,
        mode="markers",
        marker=dict(size=55, color="rgba(0,0,0,0)"),  # invisible but huge click target
        customdata=ids,
        hovertext=labels,
        hoverinfo="text",
        showlegend=False,
    ))


def _extract_clicked_block_id(event: Any) -> Optional[str]:
    """Pull the clicked block_id out of the plotly_chart selection event."""
    if not event:
        return None
    selection = getattr(event, "selection", None) or (
        event.get("selection") if isinstance(event, dict) else None
    )
    if not selection:
        return None
    points = selection.get("points") if isinstance(selection, dict) else getattr(selection, "points", None)
    if not points:
        return None
    first = points[0]
    cd = first.get("customdata") if isinstance(first, dict) else getattr(first, "customdata", None)
    if isinstance(cd, list) and cd:
        return cd[0]
    return cd if isinstance(cd, str) else None


def _exit_point(src: Dict[str, float], dst: Dict[str, float]) -> tuple[float, float]:
    """Where the arrow leaves the src block."""
    sx_center = src["x"] + src["w"] / 2
    sy_center = src["y"] + src["h"] / 2
    dx_center = dst["x"] + dst["w"] / 2
    dy_center = dst["y"] + dst["h"] / 2

    dx = dx_center - sx_center
    dy = dy_center - sy_center
    # Dominant axis
    if abs(dx) >= abs(dy):
        x = src["x"] + src["w"] if dx > 0 else src["x"]
        y = sy_center
    else:
        y = src["y"] + src["h"] if dy > 0 else src["y"]
        x = sx_center
    return x, y


def _entry_point(dst: Dict[str, float], src: Dict[str, float]) -> tuple[float, float]:
    dx_center = dst["x"] + dst["w"] / 2
    dy_center = dst["y"] + dst["h"] / 2
    sx_center = src["x"] + src["w"] / 2
    sy_center = src["y"] + src["h"] / 2

    dx = sx_center - dx_center  # from dst's POV
    dy = sy_center - dy_center
    if abs(dx) >= abs(dy):
        x = dst["x"] + dst["w"] if dx > 0 else dst["x"]
        y = dy_center
    else:
        y = dst["y"] + dst["h"] if dy > 0 else dst["y"]
        x = dx_center
    return x, y


def _format_flow(kw: float, unit_label: str) -> str:
    """Format a power-flow label. Switch to MW if large."""
    if abs(kw) >= 1000:
        return f"{kw / 1000:.2f} MW"
    return f"{kw:,.0f} {unit_label.split()[0]}"
