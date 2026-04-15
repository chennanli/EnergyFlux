# EnergyFlux Stage 1.5 — WWTP Case Study

> **First flagship case study in the broader EnergyFlux project.**
> The umbrella thesis covers multiple industrial site classes as behind-the-meter AI infrastructure hosts.
> See the [root README](../README.md) for the umbrella framing, and [`docs/site_classes.md`](../docs/site_classes.md)
> for how WWTPs compare to other industrial site classes.

---

## Can Industrial Mandatory Vacancy Ease the AI Data Center Crisis?

A case study: wastewater treatment plant buffer zones as behind-the-meter modular AI inference nodes.

---

### The problem

Building AI infrastructure at scale is breaking down on every front simultaneously.

**Grid connections** take 3–7 years through CAISO, PJM, and ERCOT interconnection queues. Over 1,000 projects are waiting in California alone. **Land near power** is being acquired by Microsoft, Google, and Amazon at a pace that prices out everyone else — retired coal plants, nuclear sites, and industrial parcels are going to hyperscalers with billions to spend. **Water for cooling** is becoming a permitting fight in drought-affected regions. **Gas turbine backup** faces 18–36 month procurement backlogs. **Centralized campuses** create single points of failure: one incident, one natural disaster, one grid event takes down inference capacity serving entire regions.

The hyperscaler playbook — find a 345 kV interconnection, build a gigawatt campus, staff it with hundreds of engineers — is not available to anyone outside the top five cloud providers. The gap between a rooftop solar install and a Microsoft megacampus covers an enormous range: a small specialty chemical plant draws 400 kW, a 30 MGD wastewater plant draws 2.5 MW, a large refinery draws 50–200 MW. Across that entire range, nobody is building distributed behind-the-meter inference infrastructure. That is what this paper is about.

---

### A different answer

Across the United States, there are over 16,000 municipal wastewater treatment plants. Every one of them is surrounded by land it **cannot build on**.

Federal and state regulations — EPA Risk Management Program, OSHA Process Safety Management, local setback codes — require industrial facilities to maintain mandatory safety buffer zones. For a typical 30 MGD plant, that means 2–5 hectares of flat, industrially-zoned land sitting permanently empty, directly adjacent to existing MW-scale electrical infrastructure, staffed around the clock, and already permitted for heavy industrial use.

This land generates no revenue. It cannot be sold. It is legally required to stay empty.

**What if we put solar panels on it?**

If the usable portion of a WWTP buffer zone — after subtracting fire access roads, exclusion zones, and maintenance clearances — can support enough PV generation to power a modular AI inference data center, then we have a site class that solves most of the problems above:

- No new grid connection (behind-the-meter, 4–7 month permit vs 3–7 years)
- No land acquisition (the land exists, is mandated to stay clear, and is industrially zoned)
- No water permit (treated effluent is already on-site for liquid cooling)
- No single point of failure (distributed across thousands of municipal sites)
- No gas turbine (solar + battery as primary, grid as backup)

---

### This simulation

This repo is a physics-informed feasibility study of exactly that idea, using a 30 MGD Bay Area municipal WWTP as the case study.

The question: can approximately 1.5 hectares of WWTP buffer land, covered with 5,700 kWp of bifacial solar panels and paired with an 8 MWh LFP battery, supply enough energy to operate a 2 MW AI inference data center — behind the meter, with no new grid interconnection?

**The simulation says yes.** 24% of total facility energy comes from solar. Daytime grid draw drops *below* today's WWTP-only baseline. Maximum night-time peak stays within a routine utility service upgrade envelope. Energy balance closes to within 0.001 kW every hour of the year.

*WWTPs are the first industrial site class we are modeling. Chemical plants, petroleum refineries, and airports present similar opportunities — different buffer zone geometries, different electrical loads, different regulatory frameworks. Future work will extend this analysis. If you have data from other site types, contributions are welcome.*

---

<!-- Replace with screenshot after running: streamlit run app.py -->
<!-- Save the Grid Impact tab as docs/images/hero_chart.png and uncomment: -->
<!-- ![Grid Impact — orange: WWTP today, blue: WWTP + solar + battery + AI data center](docs/images/hero_chart.png) -->
<!-- Caption: Orange = what the grid sees today (WWTP only). Blue = after adding 5.7 MWp solar + 8 MWh battery + 2 MW AI data center. Green zone = solar makes the plant draw *less* from the grid than before. Blue spike at night = battery charging at cheap off-peak rates. -->

---

## The result in four numbers

| | |
|---|---|
| **~24%** | of total facility energy comes from rooftop solar |
| **~2,800 kW** | maximum additional grid demand from the new system (routine 4→6 MVA upgrade) |
| **~256T tokens/yr** | inference capacity at 70% utilization (Blackwell GB200 baseline) |
| **4–7 months** | behind-the-meter permitting timeline vs. 3–7 years for a new grid connection |

---

## Why WWTPs specifically

I've been thinking about the gap between a 500 kW commercial solar install and a 1 GW hyperscale campus. A new 5 MW grid connection in California sits in a 3–7 year CAISO queue. Hyperscalers solve this by buying retired power plants with existing 345 kV interconnections — a strategy available only to Microsoft, Google, and Amazon.

There are 16,000 other sites in the US that already have MW-scale grid connections, 24/7 staffing, treated water for cooling, and heavy industrial zoning. They process municipal wastewater.

Every WWTP has what you need and nothing you don't:

| Asset | Why it matters for AI |
|---|---|
| Mandatory buffer zones (0.5–5 ha) | Empty, flat, industrially-zoned land adjacent to electrical infrastructure |
| Existing MW-scale electrical service | No new grid connection — no queue |
| Treated effluent for cooling | Liquid-cooled GPU racks without new water permits |
| 24/7 operations staff | Security and monitoring already in place |
| Heavy industrial zoning | AI data center permitted as equipment installation, not new construction |

Other site types have some of these. Closed landfills have land but not power. Rail yards have power but not cooling. Airports have land and power but residential neighbors who will fight a data center. Only WWTPs have the full stack in a single parcel already zoned for heavy industrial use.

---

## The one engineering decision that matters

**Why does the battery charge at 1 MW but discharge at 2 MW?**

The default assumption is that batteries are symmetric — charge and discharge at whatever the manufacturer allows. For an 8 MWh LFP system at this scale, that would be 2 MW each way.

Run the numbers for a 10 PM–6 AM charge window at 2 MW:

```
WWTP night load:         1,200 kW
AI data center:          2,500 kW
BESS charging at 2 MW:   2,000 kW
──────────────────────────────────
Night peak:              5,700 kW  ←  requires transformer upgrade + new easement
```

Drop the charge rate to 1 MW:

```
WWTP night load:         1,200 kW
AI data center:          2,500 kW
BESS charging at 1 MW:   1,000 kW
──────────────────────────────────
Night peak:              4,700 kW  ←  within existing service headroom
```

The battery fills the same 8 MWh over 8 hours instead of 4. It never triggers a grid upgrade. The 2 MW fast discharge is preserved for evening peak-shaving — the battery covers the full data center load for 4 hours during the $0.35/kWh on-peak window.

**The right battery for this site isn't the fastest one. It's the slowest one that can still shave the morning peak.** Asymmetric inverters exist for exactly this reason. The charge-side constraint is a ~$150k inverter sizing decision. The transformer upgrade it avoids is a ~$400k, 18-month permitting process.

---

## Quick start

```bash
pip install -r requirements.txt
PYTHONPATH=. python run_demo.py --case all
streamlit run app.py
```

Dashboard opens at `http://localhost:8501`. Three tabs:
- **Grid Impact** — the main chart: what does adding this system do to the transformer?
- **Full Year** — monthly energy balance, solar coverage %, battery SOC heatmap
- **Three Scenarios** — 24-hour stress tests: sunny day, storm + heat wave, network congestion

---

## What the simulation models

8,760 hourly steps. Every component uses physics equations, not lookup tables.

| Module | Method | Verification |
|---|---|---|
| **Solar PV** | pvlib ModelChain, real Fremont CA weather, LONGi 385W bifacial, 1P tracker | Annual yield 10,000–11,500 MWh |
| **WWTP load** | BSM1-shaped diurnal with equalization-tank smoothing † | 1,800–3,200 kW dynamic range |
| **BESS dispatch** | TOU-aware asymmetric state machine, PG&E E-20 rates | Energy balance error < 0.001 kW |
| **DC thermal** | 3-node RC ODE: chip → coolant → ambient, with derating at 80°C | Conservation error < 100 W steady-state |
| **LLM RCA** | Rule-based anomaly detection + NVIDIA NIM inference (Llama 3.1 8B) | Fires on thermal, overload, SOC, latency |

† WWTP load is a parametric curve calibrated to BSM1 operational characteristics with hydraulic dampening from an upstream equalization tank. It is not a real-time ODE solve. See Limitations.

Three 24-hour stress tests:

**Case 1 — Normal sunny day:** Solar peaks at 4,750 kW. WWTP + data center runs on free solar from 10am–4pm. Grid import drops near zero.

**Case 2 — Storm + heat wave (35°C):** Sewage surge spikes WWTP load +40%. GPU chip temperature hits 81°C. Automatic thermal derating reduces compute to 77% capacity until the storm passes. No hardware damage, no manual intervention.

**Case 3 — Overcast + network congestion:** Solar at 30% of normal. Cloud API latency spikes to 500ms. Dispatch agent shifts 100% of AI workloads to local GPUs and manages battery SOC to extend local operation.

---

## Key numbers

| Metric | Value |
|---|---|
| Site | 30 MGD Bay Area municipal WWTP |
| Solar PV | 5,700 kWp DC / 4,750 kW AC peak, bifacial 1P tracking |
| Battery | 8 MWh LFP / **1 MW charge** / **2 MW discharge** (asymmetric) |
| AI data center | 2,000 kW IT / 16 racks / 2,500 kW total (PUE 1.25) |
| Annual solar generation | ~10,660 MWh/yr |
| Solar self-sufficiency | ~24% of total facility load |
| Max grid demand increase | ~2,800 kW (routine 4→6 MVA service upgrade) |
| Permitting | **4–7 months** behind-the-meter vs. 3–7 years new interconnection |
| Token throughput (Blackwell, 70% util) | ~256 trillion tokens/yr |
| Gross revenue — Blackwell GB200 @ $0.25/M | ~$64M/yr |
| Gross revenue — Vera Rubin @ $0.25/M (est.) | ~$200–640M/yr † |
| Grid electricity cost for data center | ~$1.3M/yr |

† *Vera Rubin NVL72 estimate.* NVIDIA claims up to 10× inference throughput per watt versus Blackwell (benchmarked on Kimi K2, a specific model/sequence condition). Conservative estimate uses 3× real-world improvement; upper bound uses NVIDIA's stated 10×. No official absolute tokens/sec/MW published as of April 2026. Vera Rubin ships H2 2026. Sources: [NVIDIA GTC 2026 newsroom](https://nvidianews.nvidia.com/news/nvidia-vera-rubin-platform); [NVIDIA Tech Blog March 24 2026](https://developer.nvidia.com/blog/scaling-token-factory-revenue-and-ai-efficiency-by-maximizing-performance-per-watt/); Ming-Chi Kuo @mingchikuo on X, January 2026 (rack power supply chain).

---

## The permitting shortcut

*Behind-the-meter* means the system generates and consumes electricity entirely on-site, never selling power to the utility. That single legal distinction removes you from four regulatory regimes designed for power plants and puts you into one designed for building upgrades.

| What you avoid | Why it matters |
|---|---|
| CAISO/PJM interconnection study | Eliminates the 3–7 year queue |
| FERC filing | No wholesale electricity sales classification |
| CEQA review (California) | PV systems under 1 MW are categorically exempt |
| BAAQMD air quality permit | No combustion, no emissions |

What remains: building permit, electrical inspection, utility service upgrade. **Total: 4–7 months.**

---

## Token economics — data sources

The 5.8M tokens/sec/MW figure used in this simulation comes from Tom's Hardware's March 2025 analysis, which back-calculated from NVIDIA's published benchmarks using ~125 kW/rack (consistent with Supermicro's GB200 NVL72 datasheet: 125–135 kW operating power). It is a media-derived estimate, not a standalone NVIDIA datasheet entry.

| Hardware | Rack power | Tok/sec/MW | Annual revenue @ $0.25/M | Status |
|---|---|---|---|---|
| Blackwell GB200 NVL72 | 125–135 kW (OEM confirmed) | 5.8M (Tom's HW, Mar 2025) | ~$64M/yr | Shipping now |
| Vera Rubin NVL72 | ~190 kW Max Q (supply chain) | ~17–58M (3–10× estimate) | ~$200–640M/yr | H2 2026 |
| Vera Rubin + Groq 3 LPX | ~190+160 kW (two-rack pair) | Up to 35× Blackwell/MW | — | H2 2026 |

Key sources: [Supermicro GB200 NVL72 datasheet](https://www.supermicro.com); [NVIDIA Vera Rubin product page](https://www.nvidia.com/en-us/data-center/technologies/rubin/); [NVIDIA Groq 3 LPX page](https://www.nvidia.com/en-us/data-center/lpx/)

---

## NVIDIA stack alignment

| This simulation | NVIDIA production equivalent |
|---|---|
| 3-node RC ODE thermal model + derating | NVIDIA DCGM power capping + thermal throttle |
| Asymmetric BESS TOU dispatch | DSX Flex energy-aware workload scheduling |
| Local NIM inference routing (Llama 3.1 8B) | NVIDIA NIM on-premises deployment |
| API fallback with latency threshold | NVIDIA NIM on DGX Cloud |
| LLM anomaly RCA | NeMo Agent Toolkit orchestration |

---

## What is implemented vs future work

**In this repo:**
- 8,760-hour annual energy balance (PV + WWTP + BESS + DC)
- TOU-aware asymmetric BESS dispatch with PG&E E-20 rate structure
- RC ODE data center thermal model with automatic derating
- Network congestion routing model (local GPU vs cloud API fallback)
- LLM anomaly RCA via NVIDIA NIM (mock mode without API key)
- Streamlit dashboard — Grid Impact, Full Year, Three Scenarios

**Not yet built (future work):**
- Operator chat interface with Gemma 4 as local plant brain
- Field photo analysis for visual anomaly detection
- PLC code generation from natural language
- Full BSM1 ODE dynamic WWTP simulation
- Monte Carlo IRR across token price / utilization distributions
- Site screener across EPA NPDES public database (~16,000 US WWTPs)

---

## Project structure

```
stage1_5_wwtp_dc/
├── run_demo.py                  ← run everything from here
├── app.py                       ← Streamlit dashboard
├── requirements.txt
├── models/
│   ├── pv_generator.py          ← pvlib solar (5,700 kWp, real weather)
│   ├── wwtp_load_generator.py   ← WWTP load (BSM1-shaped, 1,800–3,200 kW)
│   ├── bess_dispatch.py         ← TOU-aware asymmetric dispatch
│   ├── dc_thermal.py            ← 3-node RC ODE thermal + derating
│   ├── inference_load.py        ← flat 2,500 kW DC load (inference is constant)
│   ├── energy_balance.py        ← physics conservation verifier
│   ├── power_flow.py            ← pandapower 5-bus (standalone verification)
│   └── network_model.py         ← API latency / congestion model
├── agent/
│   ├── dispatch_agent.py        ← anomaly detection + LLM RCA
│   └── rca_prompts.py           ← WWTP anomaly prompt templates
└── data/                        ← generated at runtime, not committed
```

---

## Limitations

**Modelling scope.** The WWTP load is a parametric diurnal curve calibrated to BSM1 characteristics — not a real-time ODE solve and not real SCADA data from a specific plant. Power flow uses a simplified 5-bus star topology; a real BTM facility shares a single internal AC bus. BESS round-trip efficiency of 0.95 is at the optimistic end; commercial LFP with inverter losses is typically 0.85–0.90. Anomaly thresholds are heuristics calibrated for demo, not operations.

**Economic assumptions.** Token revenue at $0.25/M tokens is one point in a wide distribution — current market spreads from $0.10 (commodity open-weight) to $15.00/M (premium proprietary). Revenue is highly sensitive: at $0.10/M, Blackwell yields ~$26M/yr; at $1.00/M, ~$256M/yr. IRR is dominated by token price, not energy cost. Hardware utilization (70%) for revenue and facility power draw (100%) for electricity cost measure different things at different layers — the gap is real and intentional.

**What this is not.** No site-specific engineering, no utility interconnection study, no regulatory or environmental review. This is a feasibility calculation, not a design package. A real deployment requires all of the above.

The PV physics, RC thermal ODE, and hourly energy balance are derived from first principles. Everything else is indicative.

---

## Open questions

I built this to test whether the energy balance closes. It does. But there are several things I'm genuinely uncertain about and would welcome pushback on:

1. **Is 70% serving utilization realistic at single-site 2 MW scale?** At hyperscale, batching and load balancing push utilization high. At 2 MW isolated from a larger fleet, cold-start overhead and uneven demand could drag effective utilization to 40% or lower. The economics change substantially.

2. **Does the BTM permitting pathway hold if the data center serves paying external customers?** Selling tokens commercially might reclassify the site from "energy efficiency equipment" to "commercial generator." I'm not a lawyer, and I haven't found a clear precedent. This is the legal load-bearing assumption of the whole thesis.

3. **What is the minimum viable WWTP size?** The simulation uses a 30 MGD plant. Smaller plants (5–10 MGD) exist in suburban and rural areas, often with less electrical infrastructure. At what scale does the existing transformer headroom become the binding constraint?

4. **How does this compare to retired gas peaker plants?** Peakers are another 1–20 MW BTM site class with existing interconnections. They lack cooling water but have larger grid connections. Is there a site-type comparison worth publishing?

5. **At what token price does the project break even on a 10-year DCF basis?** I ran the energy model carefully. I have not run a full DCF with capital costs, O&M, and site lease. Happy to collaborate on this with anyone who has WWTP operator data.

---

## How this fits the bigger picture

This is Scenario E from a white paper covering five industrial site types — chemical plants, refineries, airports, brownfields, and this one.

*"Distributed Industrial AI Inference Nodes: The Case for Converting Industrial Safety Buffers into Behind-the-Meter AI Factories"* — Chennan Li, PhD, PE (April 2026)

The US has ~16,000 WWTPs. Converting even 2% creates a distributed token network built in months, not years, on land that is legally required to stay empty anyway.

---

## Related

- **Stage 1** (complete): 185 kWp commercial PV + grid — `../stage1_solar_grid/`
- **Stage 2** (planned): TEP chemical plant + AI factory, 1,163 kWp, Pyomo LP dispatch
- **EnergyFlux**: `github.com/chennanli/EnergyFlux`

---

*Built by [Chennan Li](https://linkedin.com/in/chennanli), PhD, PE — energy simulation and industrial AI.*
*~20 years across GE (power plant digital twins), AspenTech (refinery simulation), NEXTracker (1M+ solar devices), and Schneider Electric (industrial LLMs at scale).*

*Questions, pushback, and WWTP operator data all welcome. I'm particularly unsure about the 70% utilization assumption and the BTM legal classification for commercial token sales — if you have relevant experience, I'd genuinely like to hear it.*
