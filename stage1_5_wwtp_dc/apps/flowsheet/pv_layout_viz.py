"""Realistic PV tracker-farm layout visualization.

Shown inside the PV block's parameter editor. The goal is: a reader who has
seen a real utility-PV site should say "yeah, that's a single-axis tracker
farm" — not "that's a placeholder rectangle."

What we draw
------------
* **Parcel boundary** (dashed gray rectangle).
* **Tracker rows** running north-south (vertical), spaced by the row pitch
  implied by GCR. Each row drawn as a thin green-blue line.
* **Module hash-marks** along each row showing where individual modules
  sit (not every module — would be too dense — but a representative density
  so the eye sees "modules on a tracker").
* **Inverter pads** as discrete orange squares distributed along the
  southern edge (access row).
* **North arrow** top-left, **scale bar** bottom-right.
* **Access road** as a lighter strip at the south edge.

We render in Plotly so it's interactive (zoom, hover) inside Streamlit.

Design assumption: single-axis horizontal trackers with N-S axis is the
industry default for utility ground-mount in the 25°–45°N band. If the user
picks fixed-tilt or dual-axis later, this viz still renders but with a note
that tracker geometry differs (TODO for v2).
"""
from __future__ import annotations

import math
from typing import Any, Dict

import plotly.graph_objects as go


def build_tracker_farm_figure(pv_block: Dict[str, Any], fig_height: int = 460) -> go.Figure:
    """Build the Plotly figure for the tracker-farm layout.

    Reads ``pv_block["outputs"]`` for the geometry + module/tracker counts
    computed by pv_tools.design_pv_array. Falls back to sensible defaults
    if outputs aren't computed yet.
    """
    out = pv_block.get("outputs", {})
    params = pv_block.get("params", {})

    dims = out.get("dimensions_m", {"width_m": 431.0, "depth_m": 216.0})
    parcel_w = float(dims["width_m"])
    parcel_d = float(dims["depth_m"])

    module_count = int(out.get("module_count", 12_000))
    gcr = float(params.get("gcr", 0.35))
    modules_per_tracker = int(params.get("modules_per_tracker", 90))
    module_w = int(params.get("module_w", 580))

    # Geometry derived from pvlib-style conventions.
    # Module chord (long side of module, portrait on tracker) ~2.4 m for 580W.
    module_chord_m = 2.4
    module_width_m = 1.2  # portrait width
    # Row pitch = module chord / GCR. (Single-axis tracker, 1-module-portrait-in-row.)
    row_pitch_m = module_chord_m / max(gcr, 0.05)

    # Leave a 10 m access road at south edge + 5 m north setback.
    access_road_m = 10.0
    north_setback_m = 5.0
    usable_depth_m = max(parcel_d - access_road_m - north_setback_m, 50.0)

    # Trackers per row (stacked N-S). Each tracker length = modules_per_tracker / 2
    # (2-high portrait) × module_width_m. Actually modules in portrait stacked two
    # high along tracker axis means tracker_length = (modules_per_tracker / 2) × module_width.
    tracker_len_m = (modules_per_tracker / 2.0) * module_width_m
    trackers_per_row = max(1, int(usable_depth_m // (tracker_len_m + 2.0)))
    # How many rows fit across parcel width?
    n_rows = max(1, int((parcel_w - 10.0) // row_pitch_m))  # 10 m east+west setback

    # Total trackers and modules actually drawn (might differ from design spec
    # because of rounding — we'll show both in the annotation).
    drawn_trackers = n_rows * trackers_per_row
    drawn_modules = drawn_trackers * modules_per_tracker

    # Inverter pads: one per ~1 MWp of array, along the south access row.
    kwp = float(out.get("kwp_dc", 0.0)) or (module_count * module_w / 1000.0)
    n_inverters = int(out.get("inverter_count_recommended", max(1, round(kwp / 1000.0))))

    fig = go.Figure()
    PARCEL_COLOR = "rgba(200,210,220,0.1)"
    ROW_COLOR = "#3FA687"
    MODULE_DOT_COLOR = "#2E7A5F"
    INVERTER_COLOR = "#E8A33D"
    ACCESS_COLOR = "rgba(130,120,100,0.35)"
    SETBACK_COLOR = "rgba(150,150,150,0.12)"

    # ── Parcel boundary ────────────────────────────────────────────────────
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=parcel_w, y1=parcel_d,
        line=dict(color="rgba(200,210,220,0.45)", width=1.5, dash="dash"),
        fillcolor=PARCEL_COLOR,
        layer="below",
    )

    # ── North setback strip ───────────────────────────────────────────────
    fig.add_shape(
        type="rect",
        x0=0, y0=parcel_d - north_setback_m, x1=parcel_w, y1=parcel_d,
        line=dict(width=0),
        fillcolor=SETBACK_COLOR,
        layer="below",
    )
    fig.add_annotation(
        x=parcel_w / 2, y=parcel_d - north_setback_m / 2,
        text="north setback",
        showarrow=False, font=dict(size=9, color="rgba(200,210,220,0.5)"),
    )

    # ── Access road (south edge) ───────────────────────────────────────────
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=parcel_w, y1=access_road_m,
        line=dict(width=0),
        fillcolor=ACCESS_COLOR,
        layer="below",
    )
    fig.add_annotation(
        x=parcel_w / 2, y=access_road_m / 2,
        text="access road · cable tray",
        showarrow=False, font=dict(size=9, color="rgba(220,200,180,0.7)"),
    )

    # ── Tracker rows ───────────────────────────────────────────────────────
    # Position rows starting from east_setback. For density, draw every row
    # when n_rows ≤ 30, else draw every other row and note in caption.
    stride = 1 if n_rows <= 30 else 2
    east_setback = 5.0
    for i in range(0, n_rows, stride):
        x = east_setback + (i + 0.5) * row_pitch_m
        if x > parcel_w - 5.0:
            break

        # Row itself as a thin vertical line over usable_depth_m
        row_bottom = access_road_m
        row_top = parcel_d - north_setback_m

        # Stack `trackers_per_row` segments with 2 m gaps between trackers.
        for k in range(trackers_per_row):
            seg_bottom = row_bottom + k * (tracker_len_m + 2.0) + 0.5
            seg_top = seg_bottom + tracker_len_m
            if seg_top > row_top:
                break
            fig.add_trace(go.Scatter(
                x=[x, x],
                y=[seg_bottom, seg_top],
                mode="lines",
                line=dict(color=ROW_COLOR, width=3.0),
                hoverinfo="skip",
                showlegend=False,
            ))

            # Module tick marks along the tracker (every 4 modules for visibility)
            n_ticks = min(modules_per_tracker // 2, 8)  # up to 8 ticks per tracker
            tick_ys = [
                seg_bottom + (j + 0.5) * (tracker_len_m / n_ticks)
                for j in range(n_ticks)
            ]
            fig.add_trace(go.Scatter(
                x=[x] * n_ticks,
                y=tick_ys,
                mode="markers",
                marker=dict(
                    symbol="line-ew",
                    size=6,
                    color=MODULE_DOT_COLOR,
                    line=dict(width=1.5, color=MODULE_DOT_COLOR),
                ),
                hoverinfo="skip",
                showlegend=False,
            ))

    # ── Inverter pads (orange squares along south access row) ──────────────
    for j in range(n_inverters):
        cx = (j + 0.5) * (parcel_w / n_inverters)
        cy = access_road_m - 3.0
        fig.add_shape(
            type="rect",
            x0=cx - 3.5, y0=cy - 2.2, x1=cx + 3.5, y1=cy + 2.2,
            line=dict(color="white", width=1),
            fillcolor=INVERTER_COLOR,
        )
    # Legend label for inverters
    fig.add_annotation(
        x=parcel_w * 0.02, y=access_road_m - 3.0,
        text=f"🟧 {n_inverters}× 550 kW central inverter",
        showarrow=False, xanchor="left",
        font=dict(size=10, color=INVERTER_COLOR),
    )

    # ── North arrow (top-left) ────────────────────────────────────────────
    arrow_x, arrow_y = 15, parcel_d - 25
    fig.add_annotation(
        x=arrow_x, y=arrow_y + 12,
        ax=arrow_x, ay=arrow_y,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True,
        arrowhead=2, arrowsize=1.4, arrowwidth=2.5,
        arrowcolor="white",
        text="",
    )
    fig.add_annotation(
        x=arrow_x, y=arrow_y + 16,
        text="<b>N</b>",
        showarrow=False,
        font=dict(size=14, color="white"),
    )

    # ── Scale bar (bottom-right) ──────────────────────────────────────────
    scale_m = 50
    sb_x0 = parcel_w - 65
    sb_x1 = sb_x0 + scale_m
    sb_y = 2
    fig.add_shape(type="line", x0=sb_x0, y0=sb_y, x1=sb_x1, y1=sb_y,
                  line=dict(color="white", width=2.5))
    fig.add_shape(type="line", x0=sb_x0, y0=sb_y - 2, x1=sb_x0, y1=sb_y + 2,
                  line=dict(color="white", width=2))
    fig.add_shape(type="line", x0=sb_x1, y0=sb_y - 2, x1=sb_x1, y1=sb_y + 2,
                  line=dict(color="white", width=2))
    fig.add_annotation(
        x=(sb_x0 + sb_x1) / 2, y=sb_y + 5,
        text=f"{scale_m} m", showarrow=False,
        font=dict(size=10, color="white"),
    )

    # ── Title + caption ───────────────────────────────────────────────────
    tracking_label = out.get("tracking_effective", params.get("tracking", "single_axis"))
    caption = (
        f"Parcel {parcel_w:.0f} × {parcel_d:.0f} m  ·  "
        f"{n_rows} rows (pitch {row_pitch_m:.1f} m, GCR {gcr:.2f})  ·  "
        f"{drawn_trackers} trackers × {modules_per_tracker} modules  ·  "
        f"{n_inverters} inverters  ·  "
        f"{tracking_label} @ {params.get('lat', 30.27):.1f}°N"
    )
    if stride > 1:
        caption = "every other row shown for clarity  ·  " + caption

    fig.update_xaxes(
        range=[-10, parcel_w + 10],
        showgrid=False, zeroline=False,
        title_text="east-west (m)",
        title_font=dict(size=10, color="rgba(200,210,220,0.6)"),
        tickfont=dict(size=9, color="rgba(200,210,220,0.6)"),
    )
    fig.update_yaxes(
        range=[-10, parcel_d + 10],
        showgrid=False, zeroline=False,
        title_text="north-south (m)",
        title_font=dict(size=10, color="rgba(200,210,220,0.6)"),
        tickfont=dict(size=9, color="rgba(200,210,220,0.6)"),
        scaleanchor="x", scaleratio=1,
    )
    fig.update_layout(
        template="plotly_dark",
        height=fig_height,
        margin=dict(l=40, r=20, t=30, b=60),
        plot_bgcolor="#0F1116",
        paper_bgcolor="#0F1116",
        title=dict(
            text=f"<span style='color:#9AA6B2;font-size:11px'>{caption}</span>",
            x=0.5, xanchor="center", y=0.98, yanchor="top",
        ),
        showlegend=False,
    )

    return fig
