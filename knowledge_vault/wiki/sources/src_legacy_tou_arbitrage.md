---
title: "Legacy note: TOU arbitrage as the BESS revenue mechanic"
authority: legacy
status: active
created: 2026-05-02
updated: 2026-05-02
informs: [bess]
scope:
  host_type: [WWTP, any]
  region: [CAISO, ERCOT, any]
  equipment: [LFP_BESS]
  voltage_level: [distribution, behind_the_meter]
  applies_when: "BESS revenue modeling for behind-the-meter colocated sites under TOU tariffs"
sources:
  - raw/wiki_legacy/bess/tou_arbitrage.md
related:
  - "[[bess_4hr_lfp]]"
  - "[[bess]]"
approved_by: null
approved_date: null
supersedes: null
---

# Legacy note — TOU arbitrage as the BESS revenue mechanic

## Source Summary

Internal design note imported from `raw/wiki_legacy/bess/tou_arbitrage.md`. Written for the EnergyFlux stage 1.5 simulation as a brief on how a BTM-colocated BESS earns revenue from time-of-use rate spreads. Single-page, US/CA-centric, 2024 numbers.

## Key Claims

- The basic mechanism: utility TOU rates differ by 3–5× between off-peak (midnight–6 AM) and on-peak (4 PM–9 PM); a BESS that charges off-peak and discharges on-peak captures the spread minus round-trip losses.
- PG&E E-20 (large commercial, CA, 2024): summer on-peak $0.35–0.42/kWh, super-off-peak $0.09–0.12/kWh, gross spread $0.23–0.30/kWh, net $0.19–0.26/kWh after 92% RTE and degradation.
- For a 2 MW / 8 MWh BESS at one full daily cycle: ~$2,000/day net, ~$510k/yr at 70% utilization, CAPEX recovery ~8 yr against $2.5M.
- Demand-charge shaving (peak kW, not kWh) can be 2–3× more valuable than TOU arbitrage; modeled separately.

## Engineering Use

- Bound the BESS revenue side of a project pro-forma when a TOU tariff is in effect. The PG&E E-20 spread is a useful first-pass assumption for any CA BTM site; for ERCOT or other markets it must be substituted with the local rate schedule.
- Sanity check: if a BESS sizing study returns a payback period >12 yr from arbitrage alone, either the TOU spread is wrong or demand-charge value is being missed.
- Pairs with the [[bess_4hr_lfp]] entity page where the 4-hour duration is justified as the right shape for the on-peak window.

## Limitations

- All numbers are CA-specific (PG&E E-20, 2024). ERCOT, MISO, NYISO, ISO-NE all have different TOU shapes (or none at all in some retail markets); do not auto-apply outside CAISO without re-grounding.
- Demand-charge modeling, capacity-credit revenue, and frequency-regulation revenue are not in this note — those are separate revenue streams the source explicitly calls "not the whole story."
- The 70% utilization assumption is a planning heuristic, not a measured outcome. Real dispatch schedules can be lower if PV co-charging is constrained or if the operator chooses to preserve cycles for capacity-credit qualification.
- 2024 numbers; PG&E rate schedules and degradation cost benchmarks change annually.

## Related

- [[bess_4hr_lfp]] — entity page where the 4-hour duration is the headline conclusion.
- [[bess]] — flowsheet block where this revenue mechanic is one of three sizing drivers.

## Informs

- BESS sizing on the revenue side: confirms the 4-hour duration choice when the dominant revenue stream is TOU arbitrage in CAISO-like markets.
- Site-level pro-forma: provides a CAISO upper-bound BESS revenue line.
- Schedule decisions: cycles per year (~250) is consistent with the 6,000-cycle LFP design life.
