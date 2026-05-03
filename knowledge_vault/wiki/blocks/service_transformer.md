---
title: "Block: Service transformer"
authority: candidate
status: active
created: 2026-05-02
updated: 2026-05-02
informs: [grid]
scope:
  host_type: [WWTP, chemical, substation, campus]
  region: [ERCOT, CAISO, PJM, MISO, NYISO, ISO-NE, any]
  equipment: [any]
  voltage_level: [distribution, behind_the_meter]
  applies_when: "service-transformer sizing and grid-coupling decisions for a BTM AI factory"
sources:
  - raw/wiki_legacy/regulations/tx_ercot_interconnect.md
related:
  - "[[wwtp_load]]"
  - "[[ai_racks]]"
  - "[[bess]]"
  - "[[src_legacy_tx_ercot_interconnect]]"
  - "[[behind_the_meter_siting]]"
approved_by: null
approved_date: null
supersedes: null
---

# Block: Service transformer

## What this block represents

The transformer that interfaces the host site to the utility distribution feeder — typically a pad-mounted or pole-mounted unit at 12.47 kV or 25 kV primary stepping down to 480 V three-phase secondary. In a BTM AI factory archetype this is **the dominant schedule risk**: the AI factory does not need a transmission interconnection, but the existing service transformer almost always needs to be upsized, and utility transformer procurement currently runs 6–18 months.

This block is also where the **non-export** configuration is enforced: PV inverters and BESS PCS are coordinated so the secondary side never pushes power upstream past the transformer.

## Key sizing variables

- **Existing transformer rating (MVA)** — the historical baseline; sized to the WWTP load with some headroom.
- **Headroom multiplier** — existing rating / WWTP peak. Tight ("lean"): 1.07×. Typical: 1.4×. Generous: 1.7×.
- **Worst-case-simultaneity peak load** — `WWTP_peak + AI_facility_load + BESS_max_charging`. This is the conservative sum the transformer must serve at one instant.
- **Required upgraded rating (MVA)** — set by worst-case peak ÷ desired transformer load factor (typically 0.8).
- **Lead time (months)** — utility-dependent; 6–9 months typical, 12–18 months in capacity-constrained territories.
- **Upgrade cost** — $200k–$800k per the [[src_legacy_dc_industry_benchmarks]] note; varies with utility tariff and territory.

## Upstream dependencies

- **[[wwtp_load]]** block: existing WWTP peak sets the baseline.
- **[[ai_racks]]** block: AI facility load adds to the peak.
- **[[bess]]** block: BESS charging adds to the peak (and BESS discharge can shave it under MPC dispatch).
- Utility tariff and territory (Oncor / PG&E / Con Ed / etc.) — sets rates, lead times, and study requirements.

## Downstream dependencies

- Distribution feeder upstream of the transformer (often the limit, not the transformer itself).
- ERCOT / CAISO / PJM interconnection rules ([[src_legacy_tx_ercot_interconnect]]).
- Project schedule: dominant schedule item in BTM colocated AI projects.

## Source notes that inform this block

- [[src_legacy_tx_ercot_interconnect]] — ERCOT-specific thresholds for new load and combined export.
- [[src_legacy_dc_industry_benchmarks]] — transformer-upgrade cost line ($200k–$800k).

## Candidate assumptions pending review

- **Lean 1.07× transformer multiplier as the default for the conservative case** — chosen because it forces a transformer-upgrade conversation; many real WWTPs are at 1.4× already, which would change the worked-case conclusion.
- **Worst-case-simultaneity peak as the sizing rule** — all three loads peaking simultaneously at maximum is conservative; a real project may justify diversity factors (peaks not co-incident) and reduce required upgrade size.
- **Lead time 6–9 months typical, 12–18 months stressed** — 2024 figures; lead times have been extending and are a moving target.
- **Upgrade cost $200k–$800k** — paraphrased from JLL/CBRE; a real project must obtain a utility quote.
- **Non-export configuration** — assumed but not designed; requires inverter firmware + EMS logic + utility approval that the block currently treats as a feature flag.

## What would make this block authoritative / reviewed

- **Reviewed**: at least one utility quote benchmarked against the assumed cost and lead time; senior electrical engineer signs off on the worst-case-simultaneity rule (or proposes a diversity-factor alternative with explicit justification); non-export configuration has an explicit one-line diagram and protection scheme.
- **Authoritative**: utility tariff documents cited directly; IEEE C57.91 / C57.96 transformer loading guides cited for the load-factor assumption; ERCOT Protocols / CAISO Tariff cited directly for interconnection thresholds. The path: promote source notes to authoritative; this block then cites them and is promoted to reviewed.
