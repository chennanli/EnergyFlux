# EnergyFlux — Blog Series Roadmap

**Author:** Chennan Li, PhD, PE
**Last revised:** 2026-04-19
**Status:** active planning doc — update as cadence shifts

---

## The series thesis

Every blog post in this series uses **the same running case study** — a behind-the-meter AI inference site colocated with a municipal wastewater treatment plant — to demonstrate one distinct capability of the modern industrial-AI engineering workflow. Together the nine posts form a full-lifecycle portfolio:

> *"I can take a real 50 MGD heavy-asset project and walk it end-to-end: AI-assisted design → physics simulation → anomaly detection → operations optimization → LLM tooling with evaluation → embedded control → drift monitoring → Bayesian sensor reconciliation. Every step uses a current AI tool, and I can explain where each tool is trustworthy and where it isn't."*

The reader's takeaway is a persona identification: **Industrial AI Engineer**. The wedge is genuinely narrow — fewer than 100 US engineers combine PhD-level domain rigor in one of refining/water/power, a PE license, modern Python/LLM production skills, and a visible writing practice. The series' job is to make that intersection legible to hiring managers at NVIDIA, OpenAI Applied, Anthropic Applied, Tesla AI Apps, and Google-X-style industrial teams.

---

## Publishing cadence

Not every post is equal weight or equal urgency. The cadence is optimized for two signals: (1) maximum compounding of SEO + LinkedIn attention in 2026 when "AI factories" is the dominant infrastructure narrative; (2) faster time-to-interview for the NVIDIA SA / applied-ML career window.

| Tier        | Target ship   | Posts           | Why this tier                                       |
|-------------|---------------|-----------------|-----------------------------------------------------|
| **Pioneer** | April–June 2026| **2, 5, 5.5**  | Highest zeitgeist fit + Genesis Mission keyword match; carry the rest |
| **Medium**  | July–Aug 2026 | **3, 6**        | Consolidate credibility; close loops opened by 2, 5 |
| **Slow**    | Sep–Nov 2026  | **4, 8, 9**     | Deep/niche; ship after momentum exists              |
| **Bonus**   | Any time      | **7**           | Standalone, not on the main arc                     |

---

## The nine posts

### 1. The BTM distributed data-center thesis  ✅ *published April 2026*
* **Hook:** Why unused WWTP buffer land is the fastest path to AI inference capacity
* **Core artifact:** Medium essay + GitHub Pages canonical
* **Links:** [`blog/blog1_v20.html`](blog/blog1_v20.html), [medium](https://medium.com/@goldfairy/turning-industrial-safety-buffers-into-ai-inference-sites-245184fab245)

### 2. GenAI-assisted design of an AI-factory site  *(Pioneer — in flight)*
* **Hook:** Traditional sizing takes 6 weeks and five vendor meetings. With an LLM + `pvlib` + a curated 15-file wiki, the same design takes 10 minutes — **and every decision is traceable to a primary source.**
* **Demo spine:** Natural-language conversation → LLM calls `pvlib` + `sizing.py` as tools → Streamlit panel updates live → RAG retrieves wiki entries → explanations cite the wiki inline. Record a screen capture; embed in the blog.
* **Technical stack:** NVIDIA NIM (Llama 3.1 70B, free tier) for the LLM; `pvlib` + custom sizing for physics; FAISS + `sentence-transformers` for RAG; Streamlit for UI. **No long-term memory** — the wiki is static and pre-curated, following Karpathy's LLM Wiki pattern (markdown files as the source of truth, LLM only *reads* at query time).
* **Deliverables:** `stage1_5_wwtp_dc/design/` (pv_tools, rag), `stage1_5_wwtp_dc/design_wiki/` (15 md), `apps/blog2_genai_app.py`, `blog2_v1.html`, Streamlit Cloud URL
* **PRD:** [`BLOG2_PRD.md`](BLOG2_PRD.md)

### 5. Flexible AI factory as a grid asset  *(Pioneer — design started)*
* **Hook:** The grid-side pain point is sub-second frequency response, and inference workloads tolerate latency much better than the grid tolerates voltage sag. **Turning "wait an extra 30 seconds during peak" into a priced product is both more humane and more technically stable than forcing the grid to solve fractions-of-a-second balancing on its own.**
* **Why this is actually new:** Everyone is talking about DC demand response; almost no one is framing *user-perceived latency as the demand-response lever*. A user who accepts a variable-latency tier for a lower price is strictly Pareto-improving vs. both fixed-price inference and grid-side curtailment.
* **Core math:** MPC / MILP dispatch via `pyomo`. Decision variables: per-hour inference utilization, BESS SOC, grid imports. Objective: maximize gross margin (token revenue × utilization × realized price tier − TOU electricity cost − BESS degradation). Constraints: SOC bounds, ramp rates, SLA floors per tier.
* **Stack:** `pyomo` with HiGHS (open-source LP/MILP), extends `stage1_5_wwtp_dc/models/dispatch_optimizer.py` that already exists
* **Deliverables:** `stage1_5_wwtp_dc/operations/`, `apps/blog5_flex_ops_app.py`, blog post

### 5.5. Surrogate models for Physical AI — from 2018 refinery calibration to 2026 AI-factory MPC  *(Pioneer — flagship, Genesis-Mission alignment)*
* **Hook:** DOE Genesis Mission's March 17, 2026 RFA ($293M) names "NN surrogates trained on validated thermo/CFD data" as a core technical approach. **I did this exact thing in 2018 at GE with the colleague who's now at NVIDIA.** 8 years ago this technique was a niche curiosity; today it's federal policy. What stayed the same, what got easier, and what the 2026 version actually looks like running on Blog 5's MPC.
* **Core artifact:** NN surrogate for the Tier A thermal model + pandapower electrical model (300-1000× speedup); GP for predictive-uncertainty calibration; chance-constrained pyomo MPC that uses the surrogates' confidence bands. The GE 2018 work + this new work form a single narrative arc.
* **Stack:** PyTorch (regression MLP), GPyTorch (GP residual modeling), pyomo (chance-constrained MPC). Data: 8,760-hour runs from Tier A + pandapower seeded with sampled workload profiles.
* **Career value:** this is the **single piece** that converts Chennan's 2018 GE joint work with the L4 NVIDIA colleague into a publicly visible credential exactly aligned with Genesis Mission's technical spine. Attach screenshot of a 2018 surrogate plot + modern NN plot side-by-side in the blog post — the "then-and-now" framing.
* **Dependencies:** needs Phase 2 (Tier A) + Phase 3 (MPC) done first so there's a physics model to surrogate. Phase 3.5 in STUDY_PLAN.md.

### 3. Dynamic validation + anomaly detection (TEP-style)  *(Medium)*
* **Hook:** A static design is a commitment letter; an 8,760-hour time-series simulation is the loan document. What happens on a hot week in July when aeration demand spikes 40% and solar is at 30%?
* **Core artifact:** Ports the TEP (Tennessee Eastman Process) anomaly-detection framework from `TEP_demo-main` onto the BTM DC time-series. Shows three classes of fault (sensor drift, setpoint mis-configuration, extreme weather) being detected and a local LLM summarizing root cause.
* **Stack:** BSM1 + pvlib + BESS ODE (existing, in `stage1_5_wwtp_dc/models/`). Anomaly detection: isolation forest + PCA reconstruction + rule-based as a three-layer ensemble. LLM RCA via NVIDIA NIM (extends existing `agent/dispatch_agent.py`).
* **Reuse:** The TEP project's structure — `data/` → `detector/` → `explain/` → `dashboard/` — maps cleanly. Don't rebuild; rename and port.

### 6. Evaluating and reducing hallucination in industrial LLM Q&A  *(Medium)*
* **Hook:** "How does the operator know when to trust the LLM?" — the question that gets every industrial-AI pilot killed. A writeup of RAG evaluation, retrieval precision, answer faithfulness, and a simple guardrail that catches the 10% of cases where the LLM would have confidently invented a wrong number.
* **Core method:** RAGAS-style eval harness (context recall, faithfulness, answer relevance). Adversarial test set — questions for which the wiki does NOT have the answer; measure how often the LLM says "I don't know" vs. hallucinates. Guardrail: every numeric answer must be grounded in a retrieved wiki chunk or tool call; else flag as low-confidence.
* **Carry-over from Blog 2:** Same LLM + wiki + tools. The eval is just a second pass over the same substrate.

### 4. Design sensitivity — inverter vs. tracker, which actually moves the needle?  *(Slow)*
* **Hook:** A contrarian empirical post. Engineers obsess over single-axis vs. fixed-tilt (a ~15% yield delta). But inverter selection and DC/AC ratio can quietly cost or save 8% on lifetime output, and that's a decision most designs default through.
* **Method:** Sobol or Morris global sensitivity analysis across 12+ design parameters. Pyomo or `SALib`. Show three surprises — the parameters that sensitivity analysis flags as most important and which ones the industry's rules-of-thumb under-weight.
* **Payoff:** A ranked table of "where to spend engineering attention for this class of site." Useful to SA teams pricing customer projects.

### 8. Model drift monitoring as industrial CI/CD  *(Slow)*
* **Hook:** The ML model that sized your site a year ago may be wrong today — module prices shift, TOU tariffs change, workload patterns evolve. Show a weekly CI run that compares the LLM's current design outputs against a frozen baseline and flags material drift.
* **Stack:** GitHub Actions + `pytest` for regression; an `eval/` folder with frozen prompts + expected outputs; drift alert triggers re-training / re-grounding the wiki.

### 9. Bayesian sensor-simulation reconciliation  *(Slow — flagship)*
* **Hook:** The oldest problem in process engineering that nobody has solved cleanly with AI yet. A plant's SCADA says flow = 48 MGD, your simulator says flow = 52 MGD. Traditionally we minimize least squares. Bayesian approach: marginalize over parameter uncertainty, put priors on sensor reliability, and let the LLM generate candidate hypotheses for which assumption is off.
* **Why this is yours:** Your chemical-engineering background + Bayesian rigor + LLM-as-hypothesis-generator is a combination less than 10 US engineers have publicly demonstrated.
* **Stack:** `pymc` or `numpyro` for Bayesian inference; LLM generates candidate parameter-correction hypotheses ranked by posterior probability.

### 7. *(Bonus, standalone)* LLMs writing production-grade PLC ladder logic
* **Hook:** Chennan's six-week field experiment. Off-the-main-arc but exceptionally rare content — the LLM-engineering × PLC intersection has maybe a dozen serious practitioners in the US.
* **Position:** Publish as a one-off Medium/GH Pages post; reference from the main series index but don't number in 1–9.

---

## Architectural choices that span the series

### Memory / knowledge model

Two tiers, Gemini's framing is correct:

| Tier                  | Role                                        | Tech                             | Which blogs                |
|-----------------------|---------------------------------------------|----------------------------------|----------------------------|
| **Static knowledge**  | Curated, pre-compiled design rules + sources| Markdown files + FAISS retrieval | 2, 3, 4, 5, 6, 8, 9        |
| **Episodic memory**   | Per-session dialog state + preferences      | LanceDB or similar vector DB     | 5, 6, and on (not Blog 2)  |

Blog 2 uses only the static tier — scope-minimal and explainable. Episodic memory enters when we start building multi-session operator tooling (Blog 5) and needs to carry user preferences across days.

### LLM provider

Default: **NVIDIA NIM** via `build.nvidia.com` free tier (Llama 3.1 70B Instruct, Nemotron 70B). Two reasons: zero-cost for the series, and tight narrative alignment with NVIDIA SA positioning.

Fallback: Claude via API or OpenAI-compatible endpoint. The design code calls through an abstraction (`design/llm.py`) so providers are swappable.

### Ground-truth data policy

Every numeric claim in a blog is either:
* Computed live from `pvlib` / `sizing.py` / `pyomo` — **traceable to the commit hash**, or
* Cited from a named primary source (EPA, NREL ATB, Lazard LCOE, PVWatts, manufacturer spec sheet) — **linked in the wiki md file**.

No numbers sourced from "I asked an LLM" unless accompanied by a grounded citation and explicit uncertainty range.

### Repo layout principle

Code for each blog's demo lives inside `stage1_5_wwtp_dc/` as a new subfolder. No new repos. This keeps the future Gemma orchestrator able to `import` every blog's tools as a single package.

---

## Dependencies and open decisions

* **EPA CWNS 2022 data access** — sandbox is egress-blocked; the data download happens on Chennan's Mac. Script scaffolding ready in `data/external/epa_cwns/`.
* **Blog 7 (PLC) scope** — user's prior field experiment; needs a short scoping conversation before write-up.
* **Post-Blog-9 vision** — Gemma 4 orchestrator as the capstone. Possibly the Kaggle Gemma 4 submission. Evaluate after Blog 6 ships.

---

## Cross-references

* [`BLOG2_PRD.md`](BLOG2_PRD.md) — Blog 2 MVP product requirements
* [`DEPLOY_RUNBOOK.md`](DEPLOY_RUNBOOK.md) — Phase A Streamlit Cloud deployment procedure
* [`docs/roadmap.md`](docs/roadmap.md) — historical / status log (what has shipped)
* [`stage1_5_wwtp_dc/README.md`](stage1_5_wwtp_dc/README.md) — case study technical overview
