# EnergyFlux Stage 1.5 — The WWTP Token Plant

> **What if a city's wastewater treatment plant could pay for itself twice — once by treating sewage, and again by running AI inference on its empty buffer land?**

This project proves the concept with a working physics simulation.

---

## The Problem

Building AI infrastructure has a hidden bottleneck: **not GPUs, but grid connections.**

In California, a new large industrial customer applying for a 5 MW grid connection faces a 3–7 year CAISO interconnection queue. Every major cloud provider is racing to acquire retired coal plants and build gigawatt campuses — a strategy that requires billions, years of permitting, and is available only to Microsoft, Google, and Amazon.

**There is an enormous gap between a 500 kW rooftop system and a 1 GW hyperscale campus.** Nobody is filling it.

---

## The Insight

Every US city has a wastewater treatment plant. Every WWTP has:

| Asset | What it means for AI |
|---|---|
| Mandatory buffer zones (0.5–5 ha) | Empty, flat, industrially-zoned land |
| Existing MW-scale electrical infrastructure | No new grid connection needed |
| Treated effluent for cooling | Water-cooled GPUs without new permits |
| 24/7 operations staff | Security and oversight already on site |
| Heavy industrial zoning | AI data center permitted as equipment installation |

Converting that buffer land to **solar + battery + AI inference** creates a distributed token factory that:

- Gets permitted in **4–7 months** (not 3–7 years)
- Operates **entirely behind the meter** — no CAISO study, no FERC filing
- Generates revenue from **AI inference tokens** on land that currently generates nothing

We call it a **Token Plant** — the inference-era equivalent of a distributed power plant.

---

## What This Simulation Does

EnergyFlux Stage 1.5 is a **physics-informed feasibility simulation** of a 30 MGD Bay Area municipal WWTP converted to host a 2 MW AI compute node.

```
                    ┌─────────────────────────────────────────────┐
                    │           10 kV Industrial Bus               │
  Utility Grid ─────┤  ┌──────┐  ┌──────┐  ┌──────┐  ┌────────┐  │
  (3 MW avg)        │  │  PV  │  │ BESS │  │ WWTP │  │   DC   │  │
                    │  │5.7MW │  │ 8MWh │  │2.5MW │  │ 2.0MW  │  │
                    │  │ SAT  │  │asym  │  │diurn │  │16 racks│  │
                    └─────────────────────────────────────────────┘
                         │            │           │          │
                    pvlib         rule-based    BSM1/     RC ODE
                   ModelChain      dispatch    synthetic   thermal
                    tracker          TOU       diurnal    3-node
                                      │
                              Dispatch Agent
                              LLM RCA (NIM/Claude)
                              local / API routing
```

Every component uses real physics equations — not assumptions, not lookup tables:

| Module | Physics | Verification |
|---|---|---|
| **Solar PV** | pvlib ModelChain, real Fremont weather | Annual yield 10,000–11,500 MWh |
| **WWTP load** | BSM1 / diurnal ODE with morning+evening peaks | 1,800–3,200 kW dynamic range |
| **BESS dispatch** | Asymmetric charge/discharge state machine | Energy balance < 0.001 kW error |
| **DC thermal** | 3-node RC ODE (chip → coolant → ambient) | Conservation error < 100 W |
| **Power flow** | pandapower 5-bus 10 kV network | Voltages 0.94–1.06 pu |
| **LLM RCA** | NVIDIA NIM / Claude dispatch agent | Anomaly detection + root cause |

---

## Key Numbers

| Metric | Value |
|---|---|
| Site capacity | 30 MGD (Bay Area medium WWTP) |
| Solar PV | 5,700 kWp DC / 4,750 kW AC peak |
| Battery | 8 MWh / 1 MW charge / 2 MW discharge (asymmetric) |
| Data center | 2,000 kW IT / 16 racks / 2,500 kW total |
| Annual solar generation | ~10,660 MWh/yr |
| Grid self-sufficiency from solar | ~24% |
| Peak grid draw (at night, BESS charging) | ~4,700 kW |
| Permitting timeline | **4–7 months** (behind-the-meter) |
| Token throughput at 70% utilization | ~256 trillion tokens/year |
| Gross revenue potential at $0.25/M tokens | ~$64M/yr |
| Grid electricity cost for DC | ~$1.3M/yr |

---

## Three Demo Cases

The simulation runs three 24-hour scenarios, each testing a different stress condition:

### Case 1 — Normal Sunny Day ☀️
A clear April day in Fremont. Solar peaks at 4,750 kW. The entire facility (WWTP + data center) runs on free solar for 6 hours straight. Battery charges midday, discharges in the evening to avoid $0.35/kWh peak rates.

**Result:** Grid import drops near zero from 10am to 4pm.

### Case 2 — Storm + Heat Wave ⛈️
July, 35°C ambient. A storm causes the WWTP aeration load to spike +40% (sewage surge). The data center is at 95% utilization. GPU chip temperature climbs to 81°C — above the 80°C derating threshold.

**Result:** Automatic thermal derating reduces compute to 77% of rated capacity. System recovers when the storm passes. No hardware damage, no manual intervention.

### Case 3 — Overcast + Network Congestion 🌐
Clouds reduce solar to 30% of normal. Simultaneously, internet congestion spikes cloud API latency to 500ms — unusable for real-time industrial inference.

**Result:** The dispatch agent detects the latency spike and shifts 100% of AI workloads to local GPUs. Response quality is maintained. Battery SOC is managed to extend local operation.

---

## Why the BESS is Asymmetric

The battery charges at 1,000 kW but discharges at 2,000 kW. This is not a mistake.

If the battery charged at 2 MW, the night-time peak grid draw would be:
```
WWTP 1,200 + DC 2,500 + BESS 2,000 = 5,700 kW → transformer upgrade required
```

With 1 MW slow charging:
```
WWTP 1,200 + DC 2,500 + BESS 1,000 = 4,700 kW → within existing service headroom
```

The fast 2 MW discharge is preserved for peak shaving — the battery can cover the full DC load for 4 hours during expensive on-peak periods. This is the core TOU arbitrage strategy.

---

## The Permitting Shortcut

"Behind-the-meter" is a legal classification, not just a description. A system that generates and consumes electricity on-site, never exporting to the grid, is classified as a **commercial customer installing energy efficiency measures** — not a generator.

This means:

| What you avoid | Why it matters |
|---|---|
| CAISO/PJM interconnection study | Eliminates 3–7 year queue |
| FERC filing | No wholesale electricity sales |
| CEQA review (California) | PV under 1 MW is categorically exempt |
| BAAQMD air quality permit | No combustion, no emissions |

Required approvals are routine: building permit, electrical inspection, PG&E service upgrade, and internal security review. **Total: 4–7 months.**

Compare this to installing a 500 kW gas turbine in Bay Area jurisdictions: 18–36 months minimum, with significant litigation risk on BAAQMD NOx permits.

---

## How the Dispatch Agent Works

```
Every hour:
  1. Read system state (T_chip, SOC, P_pv, P_wwtp, P_grid, API latency)
  2. Determine BESS action (TOU-aware state machine)
  3. Check routing: local GPU vs. cloud API
  4. Detect anomalies: thermal / WWTP overload / low SOC / congestion
  5. If anomaly: trigger LLM root cause analysis (NVIDIA NIM or Claude)
  6. Log reasoning string (always non-empty for interpretability)
```

The agent connects to NVIDIA NIM for inference. If no API key is set, it runs in mock mode — the full simulation still works.

---

## NVIDIA Stack Alignment

| This Simulation | NVIDIA Production Equivalent |
|---|---|
| 16-rack DC thermal ODE | DGX GB200 NVL72 rack-scale liquid cooling |
| Thermal derating logic | NVIDIA DCGM power capping + thermal throttle |
| Asymmetric BESS dispatch | Energy-aware workload scheduling (DSX Flex) |
| Local NIM inference routing | NVIDIA NIM deployed on-premises |
| API fallback routing | NVIDIA NIM on DGX Cloud |
| LLM RCA for WWTP anomalies | NeMo Agent Toolkit orchestration |
| Power flow (pandapower 5-bus) | Facility power management integration |
| Docker compose services | NVIDIA Container Runtime + microservices |
| Slurm scenario sweep script | DGX SuperPOD + Slurm workload manager |

---

## Quick Start

```bash
# 1. Install dependencies
cd stage1_5_wwtp_dc
pip install -r requirements.txt

# 2. Generate data and run all three demo cases
PYTHONPATH=. python run_demo.py --case all

# 3. Launch the dashboard
streamlit run app.py
```

The dashboard opens at `http://localhost:8501` with three tabs:
- **Grid Impact** — the one chart that tells the whole story
- **Full Year** — monthly energy balance, solar coverage, battery heatmap
- **Three Scenarios** — the 24-hour stress tests side by side

---

## Project Structure

```
stage1_5_wwtp_dc/
├── run_demo.py              ← Run everything from here
├── app.py                   ← Streamlit dashboard
├── requirements.txt
│
├── models/
│   ├── wwtp_load_generator.py   ← BSM1-based dynamic WWTP load
│   ├── pv_generator.py          ← pvlib solar (5,700 kWp)
│   ├── bess_dispatch.py         ← TOU-aware asymmetric dispatch
│   ├── energy_balance.py        ← Physics conservation verifier
│   ├── dc_thermal.py            ← RC ODE thermal model
│   ├── power_flow.py            ← pandapower 5-bus network
│   ├── inference_load.py        ← GPU inference load curve
│   └── network_model.py         ← API congestion model
│
├── agent/
│   ├── dispatch_agent.py        ← Rule-based + LLM RCA
│   └── rca_prompts.py           ← WWTP anomaly prompt templates
│
├── data/                        ← Generated at runtime (not committed)
│   ├── wwtp_load_hourly.csv
│   ├── pv_hourly.csv
│   ├── dispatch_hourly.csv
│   └── case{1,2,3}_results.csv
│
└── docs/
    └── slurm_scenario_sweep.sh  ← Production DGX cluster sweep
```

---

## How This Connects to the Bigger Picture

This is **Scenario E** from the white paper:
*"Distributed Industrial AI Inference Nodes: The Case for Converting Industrial Safety Buffers into Behind-the-Meter AI Factories"* — Chennan Li, PhD, PE (April 2026)

The white paper covers five scenarios — chemical plants, refineries, airports, brownfields, and this one: municipal WWTPs. The argument is that the US has ~16,000 WWTPs, each with buffer land, existing electrical infrastructure, and 24/7 staffing. Converting even 2% of them creates a distributed token network at a scale that rivals Stargate — built in months, not years, using land that is legally required to stay empty.

The simulation platform underlying the white paper is this repo.

---

## Limitations (Being Honest)

This is a feasibility demonstration, not an engineering design package.

- The WWTP load uses a synthetic physics-based diurnal signal (not real SCADA data)
- GPU costs use 2026 estimated rack pricing — these change rapidly
- Token revenue at $0.25/M tokens is a mid-market estimate; actual rates vary widely
- The power flow uses simplified 5-bus topology; real facilities are more complex
- No regulatory or environmental review has been performed on any specific site

The physics and the energy balances are real. The economic projections are indicative. A real deployment requires site-specific engineering, utility agreements, and permitting.

---

## Related

- **Stage 1** (complete, locked): Commercial PV + grid, 185 kWp — `../stage1_solar_grid/`
- **Stage 2** (planned): TEP chemical plant + AI factory, 1,163 kWp, Pyomo LP
- **White paper**: Full analysis across five industrial site types
- **EnergyFlux platform**: `github.com/chennanli/EnergyFlux`

---

*Built by Chennan Li, PhD, PE | April 2026*
*Physics-informed industrial energy simulation for the distributed AI inference era*
