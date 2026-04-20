# Blog 2 — GenAI-Assisted AI-Factory Site Design

**Status:** MVP in progress
**Owner:** Chennan Li (design, narrative); Claude (code scaffolding)
**Ship target:** Pioneer tier, April–May 2026
**Supersedes:** `stage1_5_wwtp_dc/apps/blog2_sizing_app.py` (the plain sizing dropdown stays as a simplified backup entry point)

---

## Why this blog exists

Two competing reader expectations, resolved by doing both:

1. **Industrial engineers** — want to see real physics: pvlib computing module counts, pyomo solving dispatch, sensitivity analysis that respects first principles.
2. **AI practitioners / hiring managers** — want to see a modern LLM-driven workflow: tool-calling, RAG, hallucination-resistant grounding, measurable evaluation.

Most published "GenAI for engineering" demos satisfy only one side (either a chat toy with made-up numbers, or a rigorous simulation with no AI surface). This blog satisfies both simultaneously by **making the LLM a tool-calling orchestrator over a small but real physics engine**. That's exactly the shape of work an NVIDIA SA does in the field.

---

## User journey — the demo flow

A reader clicks the embedded Streamlit URL and experiences:

```
User:   I have a 45 MGD WWTP outside Austin, TX, with 23 acres of buffer.
        How big an AI factory can I actually build there?
LLM:    [RAG: retrieves tx_ercot_interconnect.md, wwtp_buffer_setback.md]
        Three decisions drive the answer. Do you want me to pick sensible
        defaults or walk through them?
User:   Walk me through them.
LLM:    First, PV technology. At your latitude (30.27°N), single-axis tracker
        gives +18% yield vs fixed tilt but +$0.10/W CAPEX. Bifacial adds 7%
        more at GCR 0.4. Recommendation: single-axis + bifacial, 580W TOPCon.
        Sound reasonable?
User:   Yes.
LLM:    [tool call: design_pv_array(area_acres=23, module_w=580, tracking="single_axis", bifacial=True)]
        → 11,793 modules, 453 strings, 12× 550 kW inverters, 6,840 kWp DC.
        [tool call: calc_annual_yield(kwp=6840, lat=30.27, tracking="single_axis", bifacial=True)]
        → 15,200 MWh/yr (CF 25.4%).
        [RAG: single_axis_tracker.md, bifacial_gain.md]
        Your 6.8 MWp array fits in 20.7 acres; 2.3 acres left over for
        inverter pads + access roads. Next decision: hardware...
```

At every LLM turn, the right side of the Streamlit page shows:
* A **sizing-card** widget with all derived numbers (updates live)
* A **parcel layout** matplotlib plot (rectangular array on the buffer)
* A **sources panel** listing which wiki md files and tool calls fed this turn

The full transcript + updated cards are copyable — readers can export the session as a `.md` "design memo."

---

## Scope

### In scope for MVP

* **PV design via `pvlib`** — module count, string config, inverter sizing, capacity factor annual yield. **Static** (no 8760-hour simulation; that's Blog 3).
* **Hardware selection** from four options (Blackwell GB200, Vera Rubin NVL144, AMD MI300X, Cerebras WSE-3). Via wiki lookup + `sizing.py`, not a tool call per se.
* **BESS sizing** from hardware stack via existing `sizing.py` archetype constants (4h default).
* **CAPEX order-of-magnitude** — wiki lookup with source citations (Lazard, NREL ATB).
* **Revenue estimate** at four token price points (existing `sizing.py` output).
* **Natural-language chat UI** — Streamlit, NVIDIA NIM as LLM, OpenAI-compatible tool calling.
* **Static RAG** — FAISS over 15 curated markdown files. Every answer cites at least one source.
* **EPA WWTP distribution chart** as the blog's opening figure (Fig. 1).
* **Exportable design memo** — button to download the session transcript + final cards as `.md`.

### Out of scope for MVP (defer to later blogs or explicitly drop)

* **Long-term / cross-session memory** — Blog 5/6 concern. Each MVP session is independent.
* **8760-hour dynamic simulation** — Blog 3.
* **Pyomo operations optimization** — Blog 5.
* **Sensitivity analysis across design params** — Blog 4.
* **Hallucination evaluation harness** — Blog 6 (but scaffold the eval folder now).
* **Full PVsyst-style shading / albedo / soiling models** — overkill for blog demo; `pvlib` defaults with `SHADING_FACTOR`-style derates.
* **Full state-by-state interconnection rule coverage** — one state (TX) is enough for the MVP; wiki can add more later.
* **Automatic wiki maintenance (LLM-as-librarian, Karpathy pattern)** — wiki is hand-written for MVP. Auto-refresh via LLM is a Blog 6+ feature.

---

## Technical architecture

### File tree

```
stage1_5_wwtp_dc/
├── design/                                  # already exists from prior pass
│   ├── __init__.py                          # already exists
│   ├── archetypes.py                        # already exists (MGD presets)
│   ├── sizing.py                            # already exists (pure sizing fn)
│   ├── hardware_profiles.py                 # NEW — 4 GPU presets as dicts
│   ├── pv_tools.py                          # NEW — pvlib wrappers, LLM-callable
│   ├── capex.py                             # NEW — CAPEX lookup from wiki data
│   ├── llm.py                               # NEW — NIM client + tool-call loop
│   └── rag.py                               # NEW — FAISS over design_wiki/
├── design_wiki/                             # NEW — 15 curated markdown files
│   ├── _index.md                            # hand-curated map of all entries
│   ├── hardware/
│   │   ├── blackwell_gb200_nvl72.md
│   │   ├── vera_rubin_nvl144.md
│   │   ├── amd_mi300x.md
│   │   └── cerebras_wse3.md
│   ├── pv/
│   │   ├── single_axis_tracker.md
│   │   ├── bifacial_gain.md
│   │   ├── fixed_tilt.md
│   │   └── dual_axis.md
│   ├── bess/
│   │   ├── 4h_battery_standard.md
│   │   └── tou_arbitrage.md
│   ├── regulations/
│   │   ├── tx_ercot_interconnect.md
│   │   └── wwtp_buffer_setback.md
│   └── capex/
│       ├── pv_lazard_lcoe_2024.md
│       ├── bess_nrel_atb_2024.md
│       └── dc_industry_benchmarks.md
├── apps/
│   ├── blog2_sizing_app.py                  # existing, kept as "simple mode"
│   └── blog2_genai_app.py                   # NEW — the main demo
├── tests/
│   ├── test_sizing.py                       # existing
│   ├── test_pv_tools.py                     # NEW
│   └── test_rag.py                          # NEW
└── data/external/
    └── epa_cwns/
        ├── README.md                        # NEW — how to download
        └── distribution_2022.csv            # (user drops here on Mac)

blog/
├── _sources/
│   └── blog2_fig1_wwtp_distribution.png     # generated from EPA data
└── _drafts/
    └── blog2_v1.md                          # NEW — blog narrative draft
```

### Data flow (one turn of the conversation)

```
user message
  └─→ app.py: append to history
       └─→ llm.py: send history + tool schema to NIM
            ├─→ LLM decides: "I need irradiance + area inputs"
            │    ├─→ tool call: retrieve(query="Austin TX solar irradiance")
            │    │    └─→ rag.py: FAISS → returns pv/single_axis_tracker.md text
            │    └─→ tool call: design_pv_array(area_acres=23, ...)
            │         └─→ pv_tools.py: pvlib → returns dict
            ├─→ LLM composes reply using retrieved + computed data
            └─→ returns: {text, citations, tool_outputs}
       └─→ app.py: render chat bubble + update side cards + log sources
```

### LLM provider contract

* Endpoint: `https://integrate.api.nvidia.com/v1/chat/completions`
* Model: `meta/llama-3.1-70b-instruct` (default) — fallback `nv-mistralai/mistral-nemo-12b-instruct`
* Auth: `NVIDIA_NIM_API_KEY` env var; Streamlit Cloud secret
* Tool calling: OpenAI-compatible `tools` + `tool_choice=auto`
* Streaming: on, for responsive UX

### Tool schema (v1)

```json
[
  {"name": "design_pv_array",       "args": ["area_acres", "module_w", "tracking", "bifacial", "ilr"]},
  {"name": "calc_annual_yield",     "args": ["kwp_dc", "lat", "lon", "tracking", "bifacial"]},
  {"name": "compare_pv_technologies","args": ["area_acres", "lat"]},
  {"name": "size_site",             "args": ["archetype_name"]},   // existing from sizing.py
  {"name": "retrieve",              "args": ["query", "k"]},       // RAG
  {"name": "lookup_hardware",       "args": ["name"]},             // from hardware_profiles
  {"name": "lookup_capex",          "args": ["asset_type", "size"]} // from capex.py
]
```

---

## Acceptance criteria

The MVP is done when all of the following pass:

1. **Chat roundtrip with real NIM key** — user types "45 MGD WWTP in Austin, 23 acres, what can I build?" and gets a coherent design proposal with ≥3 tool calls, ≥2 wiki citations, and a live-updating side card. Transcript exportable.
2. **pvlib sanity** — `design_pv_array(area_acres=20, module_w=580, tracking='single_axis')` returns a plausible kWp within 5% of hand calculation. Locked by `test_pv_tools.py`.
3. **RAG top-k precision** — given "which PV tracking is best at 30°N?", FAISS returns `single_axis_tracker.md` in top-2. Locked by `test_rag.py`.
4. **No hallucinated numbers** — every numeric claim in the LLM's response traces back to either a tool output or a retrieved wiki chunk. A manual audit of 10 conversation transcripts finds zero ungrounded numbers.
5. **Works with no API key** — app degrades to a "mock mode" where the LLM is bypassed and the sizing/tools run directly from sidebar inputs. Ensures the deploy never fully breaks.
6. **Streamlit Cloud deploy green** — lean requirements; cold-start < 45 s.
7. **Blog 1 live-demo URL updated** — add `wwtp-genai-design.streamlit.app` (or whatever slug we get) to blog 1's GitHub Pages footer.

---

## Risks and mitigations

| Risk                                              | Likelihood | Mitigation                                                              |
|---------------------------------------------------|------------|-------------------------------------------------------------------------|
| NVIDIA NIM free tier rate-limits under traffic     | Medium     | Cache common retrievals; fall back to Nemotron or mock mode on 429     |
| pvlib deploy issues on Streamlit Cloud (numba/C)  | Low        | Pin known-good versions; mock pvlib behind a `try` if import fails     |
| Tool-calling loop gets into an infinite loop      | Medium     | Hard cap at 6 tool calls per user turn; log + return partial answer     |
| Wiki content is thin (15 files aren't enough)     | Medium     | Ship with 15; expand to 25 based on first week's conversation logs     |
| LLM invents hardware numbers despite grounding    | High       | System prompt: "If not in tool output or retrieved wiki, say you don't know." Guardrail post-processor flags uncited numbers. |

---

## Out-of-band work (on Chennan's plate, not Claude's)

* Download EPA CWNS 2022 distribution CSV to `stage1_5_wwtp_dc/data/external/epa_cwns/distribution_2022.csv` (script will tell you the URL).
* Sign up at `build.nvidia.com`, generate an API key, add to `.env` as `NVIDIA_NIM_API_KEY=...`.
* Eventual: record a 60-second demo screen capture for the blog post.

---

## Revisions

* **v1** (2026-04-19) — initial MVP PRD after aligning on GenAI-assisted design pivot.
