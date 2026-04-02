# EnergyFlux — Product Requirements Document

**Version**: 1.0
**Date**: April 2026
**Author**: Chennan Li, PhD, PE

---

## 1. Problem Statement

The energy sector faces two converging challenges. On the supply side, solar generation is intermittent and difficult to predict accurately at the device level. On the demand side, industrial facilities lack real-time visibility into how their energy consumption interacts with grid constraints.

Current tools address these problems in isolation. EnergyFlux builds a vertically integrated, physics-informed AI platform that connects solar generation forecasting, power flow analysis, and GenAI-powered root cause analysis into a single operational loop — grounded in the conservation laws that govern all physical energy systems.

**Core physical principle**: Every module in this platform enforces energy and mass balance. Physics is not a post-hoc constraint; it is the architectural foundation.

---

## 2. Goals and Success Metrics

### 2.1 Primary Goals

- Forecast solar irradiance with sub-10% MAPE at 1-hour and 24-hour horizons
- Model a representative 10-row 1P solar array using PVlib with real weather inputs
- Run power flow analysis using pandapower for a 10-node distribution network
- Trigger NVIDIA NIM-powered RCA agent when generation deviates > 15% from forecast or power flow constraints are violated
- Integrate supply-side output with TEP demand-side as a unified energy balance story

### 2.2 Success Metrics

| Metric | Target | Measurement Method |
|---|---|---|
| Irradiance forecast MAPE | < 10% at 24h horizon | Holdout test set vs. NSRDB actuals |
| Generation model accuracy | < 5% vs. PVlib reference | PVlib vs. NSRDB ground truth |
| Power flow convergence | 100% on test scenarios | pandapower runpp() success rate |
| RCA agent response time | < 8 seconds end-to-end | FastAPI endpoint timing |
| Demo completeness | Full loop runnable in < 2 min | Live demo walkthrough |

---

## 3. System Architecture

### 3.1 Four-Layer Design

| Layer | Name | Key Components | Output |
|---|---|---|---|
| Layer 1 | Forecasting | NeuralForecast (NHITS), Open-Meteo API | Hourly irradiance forecast: 24–48h horizon |
| Layer 2 | Generation Modeling | PVlib, 10-row 1P array config, temperature correction | Hourly AC power output (kWh) |
| Layer 3 | Grid Simulation | pandapower, 10–15 node distribution network | Voltage profile, line loading, constraint flags |
| Layer 4 | GenAI RCA | NVIDIA NIM (Nemotron), ReAct agent, RAG knowledge base | Structured root cause report + recommended actions |

### 3.2 Data Flow

1. Open-Meteo API delivers historical and forecast weather data (irradiance, temperature, cloud cover)
2. NeuralForecast model generates 24–48h irradiance predictions with confidence intervals
3. PVlib translates irradiance forecast into AC power output using configured array parameters
4. pandapower injects forecasted generation into the distribution network and runs power flow
5. Anomaly detector compares actual vs. forecast generation. If deviation > 15% or grid constraints are violated, RCA agent is triggered
6. ReAct agent queries weather API, RAG knowledge base, and grid model to generate a structured diagnosis

### 3.3 Integration with TEP (Demand Side)

The TEP chemical plant project represents the demand side of the same energy system. The integration point is a shared energy balance layer:

- TEP provides real-time industrial load forecast (kWh demand)
- Solar platform provides generation forecast (kWh supply)
- Balance layer computes net grid import/export requirement
- Shared RCA agent handles anomalies from both sides using the same NVIDIA NIM backend

---

## 4. Technical Specification

### 4.1 Technology Stack

| Component | Technology | Rationale |
|---|---|---|
| Irradiance Forecasting | NeuralForecast (NHITS / TimesGPT) | State-of-the-art time series, probabilistic output |
| Solar Generation Model | PVlib | Industry standard, physics-based, open source |
| Power Flow | pandapower | Python-native, active community, IEEE test networks built-in |
| LLM Inference | NVIDIA NIM (Nemotron-Ultra via API) | Demonstrates NVIDIA ecosystem, on-prem inference narrative |
| Agent Framework | LangChain ReAct | Consistent with TEP project, reusable tool architecture |
| RAG Knowledge Base | FAISS + LangChain | Lightweight, no external dependency |
| API Layer | FastAPI | Consistent with TEP project, easy to demo |
| Data Source | Open-Meteo (free API) | No API key required, global coverage, hourly resolution |
| Historical Reference | NSRDB (NREL) | Gold standard solar irradiance dataset |

### 4.2 PV Array Configuration

| Parameter | Value | Notes |
|---|---|---|
| Array configuration | 10 rows × 1P | Single-axis tracker compatible |
| System capacity | ~250 kW | Representative small commercial scale |
| Location | Fremont, CA (37.5N, 121.9W) | Aligns with developer location |
| Tilt / Azimuth | 20° / 180° (south-facing) | Optimized for Bay Area latitude |

### 4.3 Power Flow Network

A 10–15 node IEEE-style distribution network configured in pandapower:

- One external grid connection (slack bus)
- Three load buses: industrial, commercial, residential
- One PV generation bus connected to Layer 2 output
- Voltage operating range: 0.95 to 1.05 pu (ANSI C84.1 Range A)

### 4.4 RCA Agent Tool Set

| Tool | Function | Trigger Condition |
|---|---|---|
| query_weather_api() | Fetch real-time cloud cover, temperature, humidity | Always first step |
| query_rag_knowledge() | Search historical fault patterns and O&M docs | If weather doesn't explain deviation |
| query_powerflow() | Get current voltage and line loading from pandapower | If grid constraint flags are raised |
| query_equipment_specs() | Retrieve array degradation and soiling parameters | If underperformance pattern is chronic |

---

## 5. Development Plan

### 5.1 Sprint Breakdown (Stage 1 — 6 Weeks)

| Sprint | Days | Deliverable | Done When |
|---|---|---|---|
| 1 | 1–4 | Data pipeline: Open-Meteo ingestion, NSRDB download, feature engineering | Clean DataFrame with hourly irradiance ready for modeling |
| 2 | 5–8 | NeuralForecast model: NHITS training, validation, 24h forecast output | MAPE < 10% on holdout set |
| 3 | 9–12 | PVlib integration: array config, DC/AC modeling, deviation detection | Generation curve matches expected shape |
| 4 | 13–17 | pandapower network: 10-node model, PV bus, power flow, constraint flags | runpp() converges on all test scenarios |
| 5 | 18–22 | NVIDIA NIM + ReAct agent: tool definitions, RAG, structured output parser | Agent returns valid RCA JSON within 8 seconds |
| 6 | 23–28 | Integration, FastAPI, demo polish, TEP bridge layer, documentation | Full loop runs end-to-end in under 2 minutes |

### 5.2 Definition of Done (Per Module)

- Unit tests pass with > 80% coverage
- Module has a standalone runnable example script
- README section updated with setup and usage
- No hardcoded paths or API keys in committed code
- Output schema documented (input/output types explicit)

---

## 6. Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| NeuralForecast training too slow on CPU | Medium | Medium | Use pre-trained TimesGPT via API as fallback |
| pandapower power flow non-convergence | Low | High | Start with IEEE 4-node test case first |
| NVIDIA NIM API rate limits in free tier | Medium | Low | Cache RCA results; implement retry with backoff |
| Open-Meteo data gaps | Low | Medium | Pre-download 2 years NSRDB as backup |
| TEP integration scope creep | Medium | Medium | Define integration interface as simple JSON schema |

---

## 7. Interview Narrative

| Target Role Type | What This Project Demonstrates |
|---|---|
| Data Science / ML Lead | End-to-end ML pipeline ownership: ingestion → training → deployment |
| Physics-Informed AI | Physics constraints enforced at every layer: PVlib, pandapower, conservation laws |
| Energy / Grid AI | Direct applicability to solar integration challenges and utility operations |
| Industrial AI / Forward Deployed | Operational context: anomaly detection triggers action, not just reporting |
| NVIDIA Ecosystem | NVIDIA NIM used for inference layer; on-premise inference narrative |

**Core interview statement**:

> I built a physics-informed energy intelligence platform that forecasts solar generation using NeuralForecast, models grid impact using pandapower power flow, and deploys a ReAct agent on NVIDIA NIM to diagnose anomalies with structured root cause analysis. The supply side connects directly to an industrial demand-side system modeled on the Tennessee Eastman Process, creating a complete energy balance story grounded in real physics and operational data.

---

## 8. Open Questions

| Question | Owner | Due |
|---|---|---|
| Use fixed location (Fremont CA) or parameterize? | Chennan | Sprint 1 |
| Include battery storage as optional Layer 2b? | Chennan | Sprint 3 |
| TEP integration: shared FastAPI or separate services? | Chennan | Sprint 4 |
| Demo target: Jupyter notebook or running web UI? | Chennan | Sprint 6 |

---

## Appendix: Key References

- NeuralForecast: nixtla.github.io/neuralforecast
- PVlib: pvlib.readthedocs.io
- pandapower: pandapower.readthedocs.io
- NVIDIA NIM: build.nvidia.com
- Open-Meteo: open-meteo.com
- NSRDB: nsrdb.nrel.gov
