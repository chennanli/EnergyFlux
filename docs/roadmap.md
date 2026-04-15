# EnergyFlux — Roadmap

## What Is Implemented (Stage 1.5 WWTP Case Study)

| Item | Status | Notes |
|---|---|---|
| PV generation model (pvlib, real Fremont CA weather) | ✅ Done | 5,700 kWp, single-axis tracking, bifacial |
| WWTP load model (QSDsan BSM1 ODE) | ✅ Done | BSM1 steady-state solve, DO calibration, annual profile scaled from BSM1 baseline |
| TOU-aware asymmetric BESS dispatch | ✅ Done | 1 MW charge / 2 MW discharge, PG&E E-20 rates |
| DC thermal ODE (3-node RC) | ✅ Done | Chip → coolant → hot aisle, derating at 80°C |
| Network / routing model | ✅ Done | Local GPU vs cloud API fallback |
| LLM anomaly RCA | ✅ Done | NVIDIA NIM (mock mode without API key) |
| Streamlit dashboard | ✅ Done | Grid Impact, Full Year, Three Scenarios tabs |
| Energy balance verification | ✅ Done | <0.001 kW error across 8,760 hours |
| 3× 24-hour stress scenarios | ✅ Done | Normal, Storm+heat, Overcast+congestion |

---

## Near-Term (Stage 1.5 improvements)

| Item | Priority | Notes |
|---|---|---|
| Accelerated live simulator | Medium | PRD: `_internal/PRD_WWTP_LIVE_DCS_SIMULATOR.md` |
| Pyomo LP dispatch optimizer | Medium | Rule-based dispatch currently; LP would improve TOU savings |
| Monte Carlo IRR across token price / utilization | Low | Revenue sensitivity not yet modeled |
| Site screener across EPA NPDES database | Low | 16,000+ US WWTPs |

---

## Future Case Studies

| Case Study | Status | Notes |
|---|---|---|
| Chemical plant (TEP-scale, EPA RMP setback) | Planned | ~1,163 kWp, ~4 racks, Pyomo LP dispatch |
| Larger industrial campus / refinery | Future | Tens-of-MW scale, different BTM profile |
| Dedicated AI factory site | Future | Purpose-built, no legacy industrial load |

---

## Positioning Notes

- **Do not add new case studies to this repo until the WWTP case study is fully polished.**
  Priority order: BSM1 dynamic → live simulator → chemical plant.
- **Do not claim the chemical plant case study exists until code is implemented.**
- **Blog Post 4 (live simulator) should not be published until the simulator actually runs.**

---

*Last updated: April 2026*
