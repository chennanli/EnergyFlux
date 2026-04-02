# EnergyFlux · 能流

**Physics-informed AI for industrial energy systems — from generation to consumption.**

> *Conservation · Balance · Intelligence*

---

## Overview

EnergyFlux connects the full industrial energy stack using physics-first modeling and GenAI-powered diagnostics. Every module enforces energy and mass balance — physics is not a post-hoc constraint, it is the foundation.

```
Generation          Grid                Consumption
──────────────      ──────────────      ──────────────
Solar PV            Power flow          Chemical plant
BESS                Constraint check    Boiler system
Forecasting         Voltage / loading   EV charger
                         ↕
                  NVIDIA NIM Agent
            (Root cause across all layers)
```

The circle in the logo is a **control volume** — the closed boundary across which energy flows. What goes in must equal what comes out.

---

## Project Stages

### Stage 1 — Solar + Power Flow + NVIDIA NIM *(Active)*

| Module | Technology | Output |
|---|---|---|
| Irradiance forecasting | NeuralForecast (NHITS) | 24–48h forecast with confidence intervals |
| PV generation modeling | PVlib, ~250 kW 1P array | Hourly AC power output |
| Power flow simulation | pandapower, 10-node network | Voltage profile, line loading, constraint flags |
| Anomaly detection | Deviation > 15% or constraint violation | RCA trigger |
| RCA agent | NVIDIA NIM (Nemotron), ReAct + RAG | Structured root cause report |
| API | FastAPI | Forecast and diagnosis endpoints |

### Stage 2 — Battery Energy Storage + Energy Management *(Planned)*

Physics-based BESS model (SOC, charge/discharge efficiency) + Pyomo LP dispatch. Written from first principles.

### Stage 3 — Industrial Consumption Side *(Planned)*

- Chemical plant process energy consumption (TEP-based)
- Boiler system
- EV charger thermal anomaly detection
- Data center cooling load estimation

### Stage 4 — Publication *(Planned)*

Medium article series + public GitHub repo + full documentation.

---

## Repository Structure

```
EnergyFlux/
├── stage1_solar_grid/
│   ├── data/
│   ├── forecasting/
│   ├── generation/
│   ├── grid/
│   ├── agent/
│   ├── api/
│   └── notebooks/
├── stage2_bess_ems/
├── stage3_consumption/
├── configs/
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Irradiance forecasting | NeuralForecast (NHITS) |
| PV generation | PVlib |
| Power flow | pandapower |
| LLM inference | NVIDIA NIM (Nemotron-Ultra) |
| Agent framework | LangChain ReAct |
| Weather data | Open-Meteo API |
| Historical reference | NSRDB (NREL) |
| Optimization (Stage 2) | Pyomo + HiGHS |
| API | FastAPI |

---

## Getting Started

```bash
git clone https://github.com/chennanli/EnergyFlux.git
cd EnergyFlux

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Add NVIDIA_API_KEY to .env
```

---

## Contributors

Created by **Chennan Li**

| Name | Role |
|---|---|
| Chennan Li | Project lead |

---

## License

MIT
