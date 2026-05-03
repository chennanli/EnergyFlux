# flowsheet/ — block-based Aspen/ETAP-style design tool

The Blog 2 v2 UI. Replaces the chat-first `blog2_genai_app.py` (still working, kept as backup) with an **engineer-in-driver-seat** paradigm: clickable flowsheet blocks, per-block parameter editors, live recompute, LLM copilot demoted to sidekick.

## Run

```bash
cd ~/Desktop/LLM_Project/EnergyFlux
uv run streamlit run stage1_5_wwtp_dc/apps/blog2_flowsheet_app.py
```

## Why this instead of chat

Engineers using Aspen / ETAP / SAM don't type sentences at a chatbot — they click blocks, edit parameters, watch downstream numbers update. A Blog 2 demo that asks an LLM for the whole answer is a ChatGPT wrapper, not a design tool. This app puts the engineer in control; the LLM assists when asked.

## File layout

```
flowsheet/
├── __init__.py          (empty, makes it a package)
├── README.md            (this file)
├── blocks.py            (block definitions + compute functions + recompute graph)
├── canvas.py            (Plotly flowsheet rendering with click-to-select)
├── editors.py           (one editor per block type, rendered in the right panel)
├── pv_layout_viz.py     (realistic tracker-farm layout drawn inside the PV editor)
└── copilot.py           (LLM copilot panel — sees the full design, cites the wiki)
```

And the entry point:

```
apps/blog2_flowsheet_app.py   (3-column layout, wires the four modules together)
```

## Architecture

### Single source of truth

All state lives in `st.session_state.design`:

```python
{
    "pv":   {"id": "pv", "kind": "pv", "label": "PV Array",
             "params": {...}, "outputs": {...}},
    "inv":  {...},
    "bess": {...},
    "dc":   {...},
    "rack": {...},
    "wwtp": {...},
    "grid": {...},
}
```

Engineer-editable state is in `params`. Computed quantities are in `outputs` and are **always derivable** from `params` + upstream outputs. An editor never writes to `outputs` directly.

### Recompute flow

1. User clicks a block on the canvas → `st.session_state.selected_block` updates.
2. Right-panel editor renders for that block. Editing a slider/selectbox writes to `design[block_id]["params"]` and returns `True`.
3. Main app sees `changed=True` → calls `recompute_all(design)`, which walks `RECOMPUTE_ORDER` and updates every block's `outputs`.
4. Streamlit reruns → canvas, summary, and editor all show new numbers.

### Compute dependency graph

```
pv  ─────▶  inv
 │           │
 │           ▼
 ├───▶ rack ─────▶ bess
 │     │              │
 │     ▼              ▼
 ▼   (feeds dc)   (feeds dc)
wwtp  ───────▶ dc ───▶ grid
```

`RECOMPUTE_ORDER` in `blocks.py` encodes this as `["pv", "inv", "wwtp", "rack", "bess", "dc", "grid"]`. Don't reorder without checking the diagram.

### Block click → selection

Plotly canvas paints shapes (rectangles) for blocks + an invisible scatter point at each block's center carrying `customdata=block_id`. `st.plotly_chart(on_select="rerun", selection_mode=("points",))` routes clicks into the event object. `canvas._extract_clicked_block_id()` pulls the block_id back out. Main app sets `st.session_state.selected_block` and reruns.

### LLM copilot

`copilot.render_copilot_panel()` gets the full design on every turn, summarizes it into a compact text snapshot, and passes it as the system prompt prefix to NVIDIA NIM. The LLM:
* Answers questions about the current design (computing from the snapshot)
* Retrieves from `design_wiki/` via the existing `rag.py` tool
* Cannot change the design; it only explains or suggests

Tool-calling loop is the existing `design/llm.py`'s `run_tool_loop`, capped at 4 steps per copilot turn (shorter than the full demo in `blog2_genai_app.py`).

## PV layout visualization

`pv_layout_viz.build_tracker_farm_figure()` is the star viz of the demo. Draws:
* Parcel boundary (dashed)
* Tracker rows running N-S (vertical), spaced by GCR-derived pitch
* Module tick marks along each tracker
* Inverter pads (discrete orange squares) along the south access row
* North arrow, scale bar
* Access-road and north-setback strips

The layout parameters (row pitch, tracker length, row count) come from the PV block's params + outputs, so changing `module_w`, `tracking`, or `gcr` in the editor updates the viz.

## Extending

### Add a new block kind

1. Add a `_default_<kind>()` function in `blocks.py` returning the initial state.
2. Add a `_compute_<kind>()` function computing outputs from inputs.
3. Register it in `_COMPUTE_FNS` and `default_design()`.
4. Add layout entry to `BLOCK_LAYOUT` (x, y, w, h on the 12×10 abstract canvas).
5. Add color to `BLOCK_COLORS`.
6. Add headline metric formatting to `headline_metric()`.
7. Add edges to `FLOWSHEET_EDGES` if it connects to existing blocks.
8. Add `edge_flow_kw()` branch for any new edge.
9. Write an `_editor_<kind>()` function in `editors.py` and register in `_DISPATCH`.

### Add a new tool the copilot can call

Edit `stage1_5_wwtp_dc/design/llm.py` — add to `ALL_TOOL_SCHEMAS` and `ALL_TOOL_DISPATCH`. The copilot picks up new tools automatically.

## Known limitations (v1)

* Block positions are fixed — no drag-drop yet (streamlit-flow wrapper can add this later).
* No save/load design (JSON export button is present; no import yet).
* Only one load case — no seasonal / hourly sweep in v1 (that's Blog 3).
* BESS dispatch is sized but not simulated — Blog 5 adds pyomo MPC.
* Electrical model is nameplate-only — Blog 5 adds pandapower grid-to-chip.
