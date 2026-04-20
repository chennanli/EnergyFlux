# EnergyFlux — Study + Build Plan

**Owner:** Chennan Li, PhD, PE
**Last revised:** 2026-04-19
**Purpose:** the canonical main-thread document. Point any new Claude session at this file and say "follow this plan, resume from where I am" — the plan is self-contained enough to pick back up without replaying the whole conversation history.

---

## How to use this doc

1. Each **phase** is a 1–3 week work block with concrete deliverables. Work phases in order; do not skip.
2. Each phase lists (a) **what you're learning**, (b) **what you're building**, (c) **resources ranked by priority**, (d) **success criteria** — don't move to the next phase until success criteria are checked.
3. When a phase is done, tick its checkbox at the bottom of this file and drop a 3-line "what I learned" note under the phase.
4. If a new Claude session asks "where are we?" — the answer is the first phase with an unchecked success-criteria box.

---

## North star

> "End-to-end industrial AI engineer: domain rigor in water/power/refining + modern Python stack (LLM, pyomo, pvlib) + industry-trusted simulation (Modelica, EnergyPlus) + production discipline (Docker, CI/CD, eval harness)."

Every phase below exists to place one more piece of that identity on the table in a way a NVIDIA SA / OpenAI Applied / Anthropic Industrial hiring manager can verify in 15 minutes of reading.

---

## Phase 0 — Finish Blog 2 (current phase, 1–2 weeks)

**Goal:** Blog 2 live — GenAI-assisted design demo + published narrative + GitHub Pages + Medium.

**What you're learning:**
* How to structure an LLM tool-calling loop with real physics tools underneath.
* How a 15-file Karpathy-style wiki compares to brute-force RAG on raw PDFs.

**What you're building / verifying:**
* Verify `scripts/build_blog2_fig1.py` runs on your Mac and produces the expected chart.
* Get a free NVIDIA NIM key at [build.nvidia.com](https://build.nvidia.com). Export as `NVIDIA_NIM_API_KEY=nvapi-...`.
* `streamlit run stage1_5_wwtp_dc/apps/blog2_genai_app.py` locally; click each of the three starter prompts; confirm tool calls + wiki citations appear in the "Sources used" expander.
* Deploy both Streamlit apps to Streamlit Cloud per `DEPLOY_RUNBOOK.md`. Get two URLs.
* Draft `blog/_drafts/blog2_v1.md` — same voice as Blog 1, weaves Figure 1 (EPA distribution) + three demo transcripts + a short section explaining the tool-calling architecture.
* Publish: GitHub Pages first (canonical), then Medium with `rel=canonical`.

**Resources (priority order):**
1. `BLOG2_PRD.md` — the acceptance criteria
2. `DEPLOY_RUNBOOK.md` — git + Streamlit Cloud commands
3. Blog 1 published version — tone reference
4. Karpathy LLM Wiki Gist — wiki pattern reference (find via search, content not fetched)

**Success criteria:**
- [ ] Figure 1 reproduces on your Mac
- [ ] Live Streamlit demo produces a coherent design with ≥3 tool calls and ≥2 wiki citations for each of the 3 starter prompts
- [ ] Blog 2 GitHub Pages live with canonical URL
- [ ] Blog 2 Medium live with `rel=canonical` to GH Pages

---

## Phase 1 — Foundations (1 week)

**Goal:** get fluent in the vocabulary and numbers you'll use for the next 5 blogs. No code in this phase — it's reading.

**What you're learning:**
* ASHRAE TC 9.9 Thermal Guidelines — the handbook of DC cooling allowable/recommended ranges.
* Open Compute Project ORv3 rack power topology (48V / 400V DC busbar, power shelves).
* Google's "Datacenter as a Computer" (3rd ed) — flexibility-as-value thesis.
* Meta Grand Teton / OCP filings — high-density liquid-cooled rack reference.
* Modelica Buildings Library DC application package — skim the doc only.

**What you're building:**
* One-page cheat sheet per topic (5 cheat sheets total), living in `design_wiki/_learning/`. These become Blog 5 figure inputs.

**Resources (priority order):**
1. ASHRAE "Thermal Guidelines for Data Processing Environments" (4th ed) — buy or borrow; the canonical.
2. Barroso, Hölzle, Ranganathan — "The Datacenter as a Computer" 3rd ed — free online.
3. OCP ORv3 specification — [opencompute.org](https://www.opencompute.org) → Server Architecture → Rack V3.
4. LBNL "High-Performance Data Centers: A Research Roadmap" — free PDF.
5. LBNL Modelica Buildings Library `Buildings.Applications.DataCenters` docs — [simulationresearch.lbl.gov/modelica](https://simulationresearch.lbl.gov/modelica).
6. NVIDIA Vera Rubin DSX reference design — recent announcement docs.

**Success criteria:**
- [ ] Cheat sheet: ASHRAE class A1/A2/A3/A4 supply-air temps + humidity ranges
- [ ] Cheat sheet: ORv3 power bus topology diagram (hand-drawn OK)
- [ ] Cheat sheet: typical Blackwell / Rubin rack-level thermal + power numbers
- [ ] Cheat sheet: Modelica Buildings Library directory structure (where is the DC template?)

---

## Phase 2 — Tier A: Python-native detailed thermal model (2–3 weeks)

**Goal:** replace `stage1_5_wwtp_dc/models/dc_thermal.py` (current 3-node RC) with a Modelica-quality system-level dynamic model, in pure Python. This is the engine for Blogs 3 and 5.

**What you're learning:**
* `scipy.integrate.solve_ivp` for stiff systems.
* CoolProp for water/air/refrigerant thermophysical properties.
* ASHRAE 90.1 chiller part-load curves and fan-power laws.
* Digital PI/PID control with anti-windup and ramp limits.
* Fluid network topology: primary/secondary chilled water loops, cooling tower / dry cooler integration.

**What you're building (in `stage1_5_wwtp_dc/models/dc_cooling_detailed.py`):**
* `ChipNode` — GPU die thermal capacitance + derating.
* `ColdPlateNode` — direct-to-chip heat transfer (overall UA).
* `CDU` — coolant distribution unit with secondary/primary loop interface.
* `FacilityLoop` — chilled-water loop, variable-flow pumping.
* `Chiller` class with published ASHRAE part-load curve.
* `DryCooler` and `CoolingTower` with wet-bulb approach dynamics.
* `PIDController` with anti-windup, ramp limits, and setpoint bumpless transfer.
* **WWTP tertiary effluent as condenser makeup** — bonus integration (the cross-system kicker for Blog 5).
* Full-loop integration function `simulate(workload_kW_trace, T_ambient_trace, dt=10s)` returning chip / coolant / ambient temperatures.

**Validation:**
* Step test: 0 → 80% workload, watch time constants. Expected: ~30 s chip, ~120 s coolant.
* Steady-state: 1.8 MW IT + 25°C ambient should give ~ 60°C chip with standard D2C UA; 72°C with conservative sizing.
* Check energy balance < 0.1% over 24-hour sim.

**Resources:**
1. ASHRAE Handbook — HVAC Systems and Equipment, 2024 ed. Chapters on chillers (ch. 43) + cooling towers (ch. 40).
2. CoolProp docs — [coolprop.org](http://coolprop.org) — `PropsSI` function is 90% of what you need.
3. "Advanced HVAC Control" by John Seem (NREL report) — ASHRAE-style part-load curves with code.
4. Existing `stage1_5_wwtp_dc/models/dc_thermal.py` + `bess_dispatch.py` — the code style to match.

**Success criteria:**
- [ ] Module passes step-test + steady-state + energy-balance tests
- [ ] `simulate()` runs 24-hour trace in < 10 s wall time
- [ ] `test_dc_cooling_detailed.py` with ≥15 regression assertions all green
- [ ] 3-minute Loom screen-record walking through the thermal-loop diagram + a step-test plot

---

## Phase 3 — Tier A continued: pyomo MPC over the detailed model (1–2 weeks)

**Goal:** a Model Predictive Controller that takes the Tier-A model as the plant and optimizes dispatch (inference utilization, BESS SOC, grid draw) against token revenue minus electricity cost.

**What you're learning:**
* Pyomo concrete model syntax.
* HiGHS (open-source LP/MILP) vs Gurobi tradeoff.
* Receding-horizon formulation: state linearization vs nonlinear MPC.
* Shrinking-horizon end-of-day SOC target.

**What you're building (in `stage1_5_wwtp_dc/operations/`):**
* `mpc_dispatch.py` — 24-hour-horizon MILP; decision variables: hourly inference utilization, BESS charge/discharge power, grid import. Objective: maximize margin = token revenue × utilization × price_tier − grid_cost − BESS degradation. Constraints: SOC bounds, ramp rates, thermal envelope (from Tier A), SLA floor per tier.
* `latency_tier_revenue.py` — the **latency-as-demand-response** pricing function: three tiers (p50, p95, p99 latency) each with different unit revenue and different throttle tolerance.
* `mpc_runner.py` — receding-horizon harness: replan every 15 minutes using updated forecast.
* Blog 5 demo app `apps/blog5_flex_ops_app.py` — Streamlit UI showing 24-hour optimal dispatch vs rule-based (the Blog 5 headline comparison).

**Success criteria:**
- [ ] MILP solves in < 30 s on a laptop for 24-hour horizon, 15-minute step
- [ ] Vs rule-based baseline: ≥ 25% margin improvement on a typical summer day
- [ ] Demo app has a "tier mix" slider that updates the optimal plan live
- [ ] Short writeup in `blog/_drafts/blog5_v1.md` for the MPC section

---

## Phase 3.5 — Surrogate models + GP uncertainty quantification (1–2 weeks) — **flagship**

**Elevated to flagship status, 2026-04-19.** Rationale: DOE Genesis Mission's March 17, 2026 RFA ($293M) explicitly names "NN surrogates trained on validated thermo/CFD simulation data" as a **core technical approach**. Chennan's 2018 GE joint work with the now-NVIDIA L4 colleague on refinery mechanistic-model surrogation + GP uncertainty is the exact lineage. This phase lets the Blog 5 pyomo MPC run at real-time speeds (impossible with full physics) and gives Chennan a Blog 5.5 dedicated flagship post.

**What you're learning (mostly refreshing):**
* PyTorch basics — dense NN for regression.
* Gaussian Process regression for uncertainty (scikit-learn or GPyTorch).
* Model selection for surrogates — polynomial vs MLP vs ensembles.
* Chance-constrained MPC — using surrogate std deviation to make the optimizer robust.
* Active learning — when to re-train on new data regions.

**What you're building (in `stage1_5_wwtp_dc/surrogates/`):**
* `train_thermal_surrogate.py` — NN that maps `(workload, T_amb, BESS_SOC, chiller_PLR) → (T_chip, T_coolant, P_cooling)`. Training data: 8,760-hour runs from the Tier A thermal model across sampled workload profiles.
* `train_electrical_surrogate.py` — NN for pandapower: `(P_pv, P_bess, P_load) → (bus_v_min, line_loading_max, losses)`. Faster than AC power flow by 200-500x.
* `gp_uncertainty.py` — fit a GP on surrogate residuals (the 2018 GE pattern); gives calibrated predictive std for every surrogate output.
* `chance_constrained_mpc.py` — drop-in replacement for the full-physics pyomo MPC from Phase 3, now using surrogate means + stds to impose constraints with a probability margin (e.g. P(T_chip > 82°C) < 5%).
* `apps/blog55_surrogate_app.py` — Streamlit demo: side-by-side full-physics vs surrogate, with a slider for confidence level.

**Validation targets:**
* Thermal surrogate: MAPE < 2% on held-out workload profiles.
* Electrical surrogate: MAPE < 1% on bus voltages; line loading within 3%.
* GP uncertainty: empirical coverage matches nominal (80% CI actually contains 80% of test points).
* Speedup: thermal 300-1000×; electrical 200-500×.

**Blog 5.5 narrative spine:**
1. The old story: 2018 refinery mechanistic model + NN surrogate + GP uncertainty (the Chennan-Jonathan GE work). What we built, what worked, what didn't.
2. The Genesis Mission spec (quote the RFA) — same technique, national scale, 8 years later.
3. What's changed in 8 years: PyTorch > TensorFlow 1.x, transformers for multivariate time series, foundation models as priors for small-data regimes.
4. Blog 5's MPC rewritten on the surrogate — real-time, chance-constrained, traces back to every physics assumption via the surrogate's GP band.
5. Limits: out-of-distribution failure, active learning, why you still need the full physics as a periodic anchor.

**Resources:**
1. Rasmussen + Williams, "Gaussian Processes for Machine Learning" — the foundational text (free PDF).
2. PyTorch tutorials — the regression MLP ones only; avoid the transformer rabbit hole for this phase.
3. GPyTorch docs — [gpytorch.ai](https://gpytorch.ai).
4. DOE Genesis Mission RFA announcement + $293M RFA technical description (March 17, 2026).
5. Chennan's 2018 GE notebooks (if still accessible) — the historical anchor.

**Success criteria:**
- [ ] Both surrogates trained; validation metrics hit
- [ ] GP calibration check passes
- [ ] Chance-constrained MPC runs in < 3 s per planning horizon (was ~30 s with full physics)
- [ ] Blog 5.5 narrative outline drafted

---

## Phase 4 — Tier B: EnergyPlus cross-validation (1 week)

**Goal:** a DOE-certified simulator ratifies your Python thermal model. Blog 5 gets a figure that says "Python vs EnergyPlus, 24-hour trace, < 3% divergence."

**What you're learning:**
* EnergyPlus IDF file format.
* `eppy` or `pyenergyplus` Python wrappers.
* `ElectricEquipment:ITE:AirCooled` object (the DC-specific IT equipment model).
* How to drive EnergyPlus programmatically from Python.

**What you're building:**
* `stage1_5_wwtp_dc/models/energyplus_validation/` — IDF file representing the same DC as your Python model + a minimal weather file (EPW for Austin TX).
* `scripts/validate_cooling_vs_energyplus.py` — runs same 24-h workload trace through both; produces comparison plot.
* Blog 5 figure `blog/_sources/blog5_fig_validation.png`.

**Resources:**
1. EnergyPlus installation on Mac: `brew install energyplus`.
2. `eppy` (eppy-py) package — simplest Python driver.
3. EnergyPlus "Input/Output Reference" — the `ElectricEquipment:ITE:AirCooled` section.
4. NREL OpenStudio SDK (optional, heavier but more GUI-friendly).

**Success criteria:**
- [ ] `brew install energyplus` works on your Mac
- [ ] A minimal IDF simulates a 2 MW DC at steady state without errors
- [ ] 24-hour trace comparison: Python vs E+ within 3% RMS on chip temp and within 5% on total cooling energy
- [ ] Validation figure shipped in `blog/_sources/`

---

## Phase 5 — Tier C: Modelica via Docker + FMI (2–3 weeks)

**Goal:** stand up the Meta/Carrier industry-standard toolchain locally, run LBNL Buildings Library's DC model, export an FMU, load it from Python. Ship a Blog 5 figure that says "Python vs EnergyPlus vs Modelica Buildings Library — all three within 5%."

**What you're learning:**
* Docker Desktop basics on Mac — volumes, port forwarding, multi-container workflows.
* Modelica syntax (enough to read and modify models, not write from scratch).
* FMI (Functional Mock-up Interface) — how a Modelica model becomes a portable .fmu artifact.
* `fmpy` Python package for loading and simulating FMUs.
* LBNL Buildings Library directory structure and `Buildings.Applications.DataCenters` templates.

**What you're building:**
* `docker/openmodelica.Dockerfile` — slimmed Docker image with OpenModelica + Buildings Library preinstalled.
* `modelica/EnergyFluxDC.mo` — thin wrapper that sets LBNL DC template parameters to match your site.
* `scripts/build_fmu.sh` — compile the Modelica model to FMU inside the container.
* `stage1_5_wwtp_dc/models/modelica_validation/run_fmu.py` — load FMU via `fmpy`, run same 24-h trace.
* Three-way comparison figure `blog/_sources/blog5_fig_three_way_validation.png`.

**Resources (priority order):**
1. OpenModelica User Guide — [openmodelica.org/doc](https://openmodelica.org/doc).
2. LBNL Modelica Buildings Library docs — [simulationresearch.lbl.gov/modelica](https://simulationresearch.lbl.gov/modelica).
3. `Buildings.Applications.DataCenters.ChillerCooled.Paper` — the actual model file in the library; your starting template.
4. Modelica Association + FMI spec — [modelica.org/fmi](https://modelica.org/fmi).
5. `fmpy` docs — [fmpy.readthedocs.io](https://fmpy.readthedocs.io).
6. LBNL paper: Wetter, Fuchs, "Buildings Library" — the foundational paper.

**Success criteria:**
- [ ] Docker image builds and `omc --version` runs inside
- [ ] `Buildings.Applications.DataCenters.ChillerCooled.Paper` compiles inside the container
- [ ] FMU exports successfully
- [ ] `fmpy.simulate_fmu()` drives the FMU with the same workload trace Phase 2 uses
- [ ] Three-way comparison figure in `blog/_sources/`: Python vs EnergyPlus vs Modelica all within 5% RMS

---

## Phase 6 — Grid-to-Chip electrical model (pandapower, ETAP-equivalent) (2 weeks)

**Upgraded from a 1-week appendix to a 2-week first-class Blog 5 component.** Rationale: in March 2025 ETAP + Schneider + NVIDIA launched the first "Grid-to-Chip" electrical digital twin for AI factories on Omniverse. Electrical-side fluency is now as important as thermal for NVIDIA SA positioning. You don't have ETAP access (commercial, ~$50k/seat), but `pandapower` is the peer-reviewed open-source equivalent used by TU Dortmund and Fraunhofer IEE — covers ~90% of ETAP's functions. Your stage 1 already has a 5-bus pandapower model; this phase extends it to full grid-to-chip depth.

**Narrative hook for Blog 5 and future job conversations:** "I can't license ETAP, so I built the equivalent BTM AI-factory grid-to-chip model in pandapower. Physics is identical, only GUI and certification differ." This is a much stronger positioning than claiming ETAP fluency you can't verify.

**What you're learning:**
* Medium-voltage distribution design: 138 kV → 25 kV → 10 kV → 480 V → 400 V DC → 48 V DC.
* Short-circuit analysis (symmetric + asymmetric faults, IEC 60909).
* Protection coordination: overcurrent curves, selectivity, fuse-breaker-relay sequencing.
* Arc flash energy calculation (IEEE 1584) — the thing that gets you fired from real DC work.
* Harmonic load flow — why GPU rectifiers inject harmonics and what filters do about it.
* AC/DC converter modeling in pandapower's `converter` object.
* How grid events (transformer trip, voltage sag, frequency excursion) couple into thermal behavior — the cross-domain story almost no one tells in public.

**What you're building (all in `stage1_5_wwtp_dc/models/electrical/`):**
* `grid_to_chip_network.py` — extended pandapower network with 6 voltage levels:
  - 138 kV utility slack (with short-circuit source impedance)
  - 138/25 kV utility substation transformer + overcurrent protection
  - 25 kV primary distribution (existing 5-bus feeder logic)
  - 25/0.48 kV service transformer + arc-flash-bounded switchgear
  - 480 V AC → 400 V DC rectifier (modeled via pandapower `converter` element)
  - Aggregated 48 V DC rack load (lumped at 400 V DC bus for simplicity)
* `short_circuit_study.py` — IEC 60909 3-phase + line-to-ground fault at every bus; outputs a table of available fault currents.
* `protection_coordination.py` — overcurrent curves at each level; validates time-current coordination.
* `arc_flash_study.py` — IEEE 1584 energy calc at each switchgear location; outputs PPE category per ASTM F1959.
* `harmonic_analysis.py` — injects a canonical GPU-rectifier harmonic spectrum; checks THD at PCC.
* `electrical_thermal_coupling.py` — the killer demo: inject a 25 kV transformer trip event, watch 400 V DC bus voltage sag, downstream rectifier derate, GPU undervolt-protection triggered, thermal envelope response. Uses your Tier A thermal model.
* `apps/blog5_electrical_app.py` — Streamlit page showing single-line diagram + fault scenarios + coupling with thermal.

**Blog 5 figures this phase produces:**
* `blog5_fig_single_line_diagram.png` — the grid-to-chip SLD (Schneider/ETAP style)
* `blog5_fig_arcflash_study.png` — energy levels at each switchgear location
* `blog5_fig_electrical_thermal_coupling.png` — transformer trip → thermal response timeline

**Resources (priority order):**
1. pandapower official docs — [pandapower.org](https://www.pandapower.org) — tutorials especially.
2. pandapower GitHub — [github.com/e2nIEE/pandapower](https://github.com/e2nIEE/pandapower) — example notebooks are the fastest learning path.
3. IEEE 1584-2018 — Arc Flash Hazard Calculations.
4. IEC 60909 — Short-circuit currents in 3-phase AC systems.
5. ETAP online reference model — [etap.com/articles/smart-data-center](https://etap.com/articles/smart-data-center) — what ETAP does, we mirror.
6. ETAP + Schneider + NVIDIA March 2025 announcement — read to understand exactly what workflow NVIDIA expects.
7. OCP ORv3 Server Power Shelf specification — the 48 V DC side.
8. Schneider Electric White Paper 127, "400V DC in the Data Center" — free PDF.
9. Google Urs Hölzle 48 V DC history talks on YouTube.

**Success criteria:**
- [ ] Extended 10+ bus pandapower network builds and solves with `runpp` and `runpp_3ph`
- [ ] Short-circuit study produces fault-current table matching hand-calculation within 5%
- [ ] Arc flash study outputs PPE category for every bus
- [ ] Harmonic analysis shows THD < 5% at PCC after simulated passive filter
- [ ] Electrical-thermal coupling demo: sane behavior under transformer-trip event
- [ ] Three Blog 5 figures shipped to `blog/_sources/`
- [ ] Can narrate in 90 seconds: "here's what ETAP does for AI factories; here's how my pandapower model mirrors each function; here's where I'd use real ETAP vs this"

**Career-positioning artifact (the deliverable that unlocks interviews):**
A one-page PDF titled **"ETAP-equivalent AI factory electrical design in open-source pandapower"** with:
* A side-by-side function table (ETAP module → pandapower module → your stage1 implementation)
* A screenshot of your SLD + fault study
* A link to the Streamlit demo
* A claim: "Given ETAP on day 1 of a role, I port this design in a week."

This one-pager goes into your GitHub profile and LinkedIn. It's your electrical-side proof-of-work.

**What about DeepMind Tapestry?**
Don't build around it. Tapestry (Google X moonshot) targets transmission-level interconnection queue optimization — a different layer than AI-factory electrical design. PJM deployment is real; 86% sim-speed gain is real. But for your BTM AI-factory topology it's not on the critical path. **Know it as conversation currency**, not something to mirror.

---

## Phase 7 — Write, ship, and promote Blog 5 (1 week)

**Goal:** Blog 5 published (GitHub Pages canonical + Medium), LinkedIn amplification, Twitter/X for NVIDIA SA visibility.

**What you're building:**
* `blog/blog5_v1.md` — narrative weaving the latency-as-DR thesis + the three-way validated model + the pyomo MPC results.
* Three figures: (1) EPA distribution reference back to Blog 2, (2) Python-vs-E+-vs-Modelica 3-way validation, (3) rule-based vs MPC margin comparison.
* `blog/github_pages/posts/05-flex-ai-factory/` following Blog 1's pattern.
* 60-second screen-capture of the Blog 5 demo app.

**Success criteria:**
- [ ] Blog 5 live on GitHub Pages (canonical) and Medium (with `rel=canonical`)
- [ ] ≥1 DM from someone at NVIDIA / Anthropic / OpenAI / hyperscaler within 2 weeks of posting
- [ ] LinkedIn post with ≥50 engagements

---

## Phase 8+ — (placeholder) Blogs 3, 6, 4, 8, 9

Deferred until Blog 5 is live and the Blog 5 momentum is assessed. See `ROADMAP.md` for the 9-blog arc and publishing cadence.

---

## Tool and library inventory

### Mac-native
* Python 3.11 + `uv` for env management
* `streamlit`, `pandas`, `numpy`, `plotly`, `matplotlib`, `openai` — Blog 2 ships on these
* `scipy`, `coolprop`, `pyomo`, `highspy` — Phase 2+3
* `eppy` + EnergyPlus via `brew install energyplus` — Phase 4
* `fmpy` — Phase 5 FMU integration

### Docker
* `openmodelica/openmodelica:latest` image — Phase 5
* `brew install --cask docker` — Docker Desktop on Mac

### Commercial/free but off-Mac
* LBNL Modelica Buildings Library — free, open-source, runs inside the Docker image
* NVIDIA NIM via `build.nvidia.com` — free tier, OpenAI-compatible endpoint
* NVIDIA Omniverse DSX — aspirational; needs RTX GPU + license, not attempting

### Intentionally NOT using
* LangChain / LangGraph — `design/llm.py` is 80 lines of plain Python, keep it readable
* LanceDB / memory-lancedb-pro — not needed until Blog 5/6 when episodic memory matters
* Dymola — commercial Modelica tool; OpenModelica + Docker gets 90% of the value for zero dollars
* Ansys Fluent / Icepak — CFD is overkill for our system-level model

---

## References (persistent reading list)

### DC cooling + controls
* Wetter et al., "Modelica Buildings Library", J. Building Performance Simulation, 2014 + annual updates
* Zhang, Wetter et al., "Modelica Models for Data Center Cooling Systems", SimBuild 2018 — the foundational paper for `Buildings.Applications.DataCenters`
* LBNL Berkeley Lab data-center research portal
* ASHRAE TC 9.9 publications (various)

### Power topology
* Open Compute Project specs
* Schneider Electric White Paper 127, 400V DC in DC
* NVIDIA Vera Rubin DSX reference design

### LLM / tool calling
* Karpathy LLM Wiki Gist (original)
* NVIDIA NIM docs at `docs.nvidia.com/nim`
* OpenAI tool-calling API reference

### Optimization
* Pyomo documentation
* HiGHS solver — [highs.dev](https://highs.dev)

---

## Cross-refs

* [ROADMAP.md](ROADMAP.md) — 9-blog publishing arc
* [BLOG2_PRD.md](BLOG2_PRD.md) — Blog 2 MVP PRD
* [DEPLOY_RUNBOOK.md](DEPLOY_RUNBOOK.md) — deployment procedure
* `stage1_5_wwtp_dc/design/` — Blog 2 design engine
* `stage1_5_wwtp_dc/models/` — dynamic sim backbone (Blog 3+)
* `stage1_5_wwtp_dc/operations/` — pyomo MPC (Blog 5, to be created)

---

## Phase progress tracker

```
[ ] Phase 0   — Finish Blog 2
[ ] Phase 1   — Foundations (ASHRAE, OCP, LBNL)
[ ] Phase 2   — Tier A: Python detailed thermal model
[ ] Phase 3   — Tier A continued: pyomo MPC
[ ] Phase 3.5 — Surrogate models + GP uncertainty (FLAGSHIP)
[ ] Phase 4   — Tier B: EnergyPlus validation
[ ] Phase 5   — Tier C: Modelica via Docker
[ ] Phase 6   — HVDC power topology (pandapower grid-to-chip)
[ ] Phase 7   — Write + publish Blog 5 AND Blog 5.5
```

When a phase is done, change `[ ]` to `[x]` and add a 3-line "what I learned" note above this tracker.
