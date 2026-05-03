---
title: "Block: BESS"
authority: candidate
status: active
created: 2026-05-02
updated: 2026-05-02
informs: [bess]
scope:
  host_type: [WWTP, chemical, substation, campus]
  region: [CAISO, ERCOT, any]
  equipment: [LFP_BESS]
  voltage_level: [distribution, behind_the_meter]
  applies_when: "battery energy storage sizing for BTM colocated AI inference sites"
sources:
  - raw/wiki_legacy/bess/4h_battery_standard.md
  - raw/wiki_legacy/bess/tou_arbitrage.md
  - raw/wiki_legacy/capex/bess_nrel_atb_2024.md
related:
  - "[[bess_4hr_lfp]]"
  - "[[src_legacy_4h_battery_standard]]"
  - "[[src_legacy_tou_arbitrage]]"
  - "[[src_legacy_bess_nrel_atb_2024]]"
  - "[[inverter]]"
  - "[[service_transformer]]"
approved_by: null
approved_date: null
supersedes: null
---

# Block: BESS

## What this block represents

The battery energy storage system that smooths PV–load mismatch, captures TOU arbitrage, shaves peak demand, and (optionally) provides capacity-credit revenue. Blog 2 default: **4-hour LFP** at 2.62 MW / 10.5 MWh for the 45 MGD archetype. The flowsheet treats this as one block but it physically includes cells, BMS, PCS (power-conversion-system inverter), thermal management, and fire suppression.

The detailed entity-level synthesis is on [[bess_4hr_lfp]]; this block page describes the role in the flowsheet and the sizing variables.

## Key sizing variables

- **Power rating (MW)** — set by peak demand-shaving requirement plus PV-mismatch smoothing.
- **Energy rating (MWh)** — power × duration. Default duration 4 hours ([[src_legacy_4h_battery_standard]]).
- **Round-trip efficiency** — ~92% LFP at moderate C-rate.
- **Cycle life** — ~6,000 cycles at 80% DoD; planning horizon 20 years with augmentation at year 10.
- **Maximum charge/discharge ratio** — affects worst-case-simultaneity peak grid demand calculation.
- **CAPEX** — $230–320/kWh installed (4-hour LFP, [[src_legacy_bess_nrel_atb_2024]]).
- **Augmentation reserve** — ~$40/kWh budgeted at year 10 to maintain rated capacity through year 20.

## Upstream dependencies

- **[[pv_array]]** block: surplus PV energy is the primary charge source.
- Grid: secondary charge source during off-peak TOU windows.
- **[[wwtp_load]]** + **[[ai_racks]]**: the load profile that the BESS smooths.

## Downstream dependencies

- **[[service_transformer]]** block: BESS charging adds to peak transformer demand. Worst-case-simultaneity peak = AI rack load + WWTP load + BESS charging power.
- **[[ai_racks]]** block: BESS provides ride-through during PV downtime or grid disturbances.
- TOU revenue stream: BESS discharges during on-peak windows ([[src_legacy_tou_arbitrage]]).

## Source notes that inform this block

- [[src_legacy_4h_battery_standard]] — duration choice (4 hours).
- [[src_legacy_tou_arbitrage]] — revenue mechanic on the TOU side.
- [[src_legacy_bess_nrel_atb_2024]] — CAPEX trajectory and augmentation reserve.
- [[bess_4hr_lfp]] — entity-level synthesis combining the above.

## Candidate assumptions pending review

- **4-hour duration** — the right answer in CAISO and ERCOT under current capacity-credit rules; not yet validated under PJM, MISO, NYISO, ISO-NE.
- **LFP chemistry** — chosen for fire-code envelope (NFPA 855) and cycle life. NMC and LFP have different pros/cons; promotion requires either ATB re-grounding or a chemistry-comparison page.
- **Round-trip efficiency 92%** — a planning heuristic; real systems show degradation over time and lower RTE at extreme C-rates or temperature.
- **Charge/discharge ratio for worst-case-simultaneity** — currently 0.5 (BESS charging at half of discharge nameplate); the right number depends on PV-coupled vs grid-charging split, and a real project must justify this.
- **CAPEX range $230–320/kWh** — 2024–2025 utility-scale; small-project + BTM premium can be 15–30% higher.

## What would make this block authoritative / reviewed

- **Reviewed**: source notes promoted; senior engineer signs off on the 4-hour-LFP-default decision rule for the specific market the project sits in. CAPEX numbers cross-checked against at least one BESS RFQ. Worst-case-simultaneity charge/discharge ratio justified explicitly per project.
- **Authoritative**: NREL ATB worksheet directly cited, FERC Order 2222 and follow-on capacity-credit rulings explicitly cited, NFPA 855 cited for fire-code envelope. The path: promote source notes to authoritative, then this block to reviewed.
