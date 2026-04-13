# Stage 1.5 — WWTP Municipal AI Compute Node

A physics-informed simulation proving that municipal wastewater treatment plants can host behind-the-meter PV + BESS + AI inference data centers. Every US city has a WWTP with buffer zones, MW-scale electrical infrastructure, and treated effluent for cooling — converting this land to distributed AI compute nodes addresses grid interconnection bottlenecks (3-7 year CAISO queue → 4-7 month BTM approval).

This is Scenario E from the white paper: *"Distributed Industrial AI Inference Nodes: The Case for Converting Industrial Safety Buffers into Behind-the-Meter AI Factories"* by Chennan Li, PhD, PE | EnergyFlux | April 2026.

## Architecture

```
                    ┌─────────────────────────────────────────────┐
                    │           10kV Industrial Bus                │
                    │  ┌──────┐  ┌──────┐  ┌──────┐  ┌────────┐  │
  Utility Grid ─────┤  │  PV  │  │ BESS │  │ WWTP │  │   DC   │  │
  (3 MW avg)        │  │5.7MW │  │ 8MWh │  │2.5MW │  │ 2.5MW  │  │
                    │  │ SAT  │  │asym  │  │diurn │  │16 rack │  │
                    │  └──────┘  └──────┘  └──────┘  └────────┘  │
                    └─────────────────────────────────────────────┘
                         │            │           │          │
                    ┌────┴────┐  ┌────┴────┐ ┌────┴───┐ ┌───┴────┐
                    │pvlib    │  │Rule-    │ │BSM1/   │ │RC ODE  │
                    │ModelChain│  │based    │ │synth.  │ │thermal │
                    │tracker  │  │dispatch │ │diurnal │ │3-node  │
                    └─────────┘  └─────────┘ └────────┘ └────────┘
                                      │
                              ┌───────┴────────┐
                              │ Dispatch Agent  │
                              │ LLM RCA (Claude)│
                              │ Local/API route │
                              └────────────────┘
```

## Quick Start

```bash
cd stage1_5_wwtp_dc/

# Install dependencies
uv pip install -r requirements.txt

# Generate annual data + run all 3 demo cases
PYTHONPATH=. python run_demo.py --case all

# Launch dashboard
streamlit run app.py
```

## Key Findings

**Case 1 — Normal Operations:** PV covers ALL loads for 4-6 hours midday. BESS slow-charges overnight (1 MW), fast-discharges morning peak (2 MW). Grid averages ~3 MW, night-weighted.

**Case 2 — Thermal Stress:** At 35°C ambient + 95% DC utilization, T_chip reaches 81°C triggering thermal derating to 77% load. Storm-event WWTP spike to 3,100 kW handled by BESS discharge + grid.

**Case 3 — Network Congestion:** API latency exceeding 200ms forces 100% local inference routing. T_chip rises due to increased local compute. Agent monitors headroom and BESS SOC.

## NVIDIA Stack Mapping

| Stage 1.5 Demo Component            | NVIDIA Production Equivalent               |
|--------------------------------------|---------------------------------------------|
| 16-rack DC simulation (RC ODE)       | DGX GB200 NVL72 rack-scale liquid cooling   |
| Thermal derating logic               | NVIDIA DCGM power capping + thermal throttle|
| Asymmetric BESS dispatch (1MW/2MW)   | Energy-aware workload scheduling (DSX Flex)  |
| Local inference routing (NIM)        | NVIDIA NIM deployed on-premises              |
| API fallback routing                 | NVIDIA NIM on DGX Cloud / external endpoint  |
| LLM RCA for WWTP anomalies          | NeMo Agent Toolkit orchestration             |
| Network congestion model             | Spectrum-X tail latency environment          |
| Power flow (pandapower 5-bus)        | Facility power management integration        |
| Docker compose services              | NVIDIA Container Runtime + microservices     |
| Slurm scenario sweep script          | DGX SuperPOD + Slurm workload manager        |

## Production Deployment

The simulation modules are independently runnable and composable via Docker Compose (see `docker-compose.yml`). For production Monte Carlo sweeps, see `docs/slurm_scenario_sweep.sh` — a Slurm array job script running 1,000 BSM1 scenarios on DGX Cloud with container-based reproducibility.

## Disclaimer

**THIS IS A FEASIBILITY DEMO.** The NVIDIA components listed above are production deployment targets. This demo proves the physical and operational concept is viable at MW scale using first-principles modeling. Actual deployment requires NVIDIA AI infrastructure, utility service agreement, and regulatory permitting (~4-7 months BTM approval).

## Related Work

- White paper: *"Distributed Industrial AI Inference Nodes"* — Chennan Li, PhD, PE (April 2026)
- EnergyFlux Platform: [github.com/EnergyFlux](https://github.com/EnergyFlux)
- Stage 1 (Commercial PV + Grid): `../stage1_solar_grid/` (complete, locked)
