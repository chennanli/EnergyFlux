# stage1_5_wwtp_dc — Blog 2 demo

The Blog 2 demo: a flowsheet for first-pass sizing of a behind-the-meter
inference site at an industrial host (the worked case is a municipal WWTP),
plus a chat copilot that retrieves from an engineer-governed knowledge base.

This folder is the code that goes with [Blog 2](../README.md). The Blog 1
thought piece is linked from the root README; it is a thesis post and has
no companion simulation code in this repo.

---

## What's in here

| Path | What it is |
|---|---|
| [`apps/blog2_flowsheet_app.py`](apps/blog2_flowsheet_app.py) | Streamlit flowsheet UI — pick blocks (PV, BESS, DC, grid), see sizing roll up |
| [`apps/blog2_genai_app_v2.py`](apps/blog2_genai_app_v2.py) | Streamlit chat — copilot that calls the sizing tools and cites the vault |
| [`apps/blog2_sizing_app.py`](apps/blog2_sizing_app.py) | Smaller archetype-only sizing app (30/40/50/60 MGD presets) |
| [`apps/flowsheet/`](apps/flowsheet/) | Flowsheet building blocks, canvas, editors |
| [`design/archetypes.py`](design/archetypes.py) | The four registered WWTP archetypes |
| [`design/sizing.py`](design/sizing.py) | Sizing math (PV → BESS → DC → revenue) |
| [`design/pv_tools.py`](design/pv_tools.py) | PV array sizing + tracker comparison |
| [`design/rag_v2.py`](design/rag_v2.py) | Vault-backed retrieval with authority filtering |
| [`design/llm_v2.py`](design/llm_v2.py) | NVIDIA NIM client + tool-calling loop |
| [`tests/`](tests/) | Regression tests for sizing + PV tools |

The knowledge base lives one level up at [`../knowledge_vault/`](../knowledge_vault/);
the rendered HTML version lives at [`../wiki/`](../wiki/).

---

## Run the demo

```bash
pip install -r requirements.txt
export NVIDIA_API_KEY=<your_nvidia_api_key>
streamlit run apps/blog2_genai_app_v2.py
```

The flowsheet UI runs the same way:

```bash
streamlit run apps/blog2_flowsheet_app.py
```

---

## Authority discipline

Every retrieval hit carries an `authority` field — `authoritative`,
`reviewed`, `candidate`, or `legacy`. The chat copilot is told to cite
authoritative + reviewed pages as primary, and to label anything it pulls
from a candidate or legacy page as "pending review" until a senior
engineer signs off. The pattern is documented in
[`../knowledge_vault/AGENTS.md`](../knowledge_vault/AGENTS.md).

---

## Tests

```bash
cd ..
pytest stage1_5_wwtp_dc/tests/ -v
```
