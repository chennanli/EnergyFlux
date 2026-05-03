---
title: "Block: WWTP load"
authority: candidate
status: active
created: 2026-05-02
updated: 2026-05-02
informs: [wwtp]
scope:
  host_type: [WWTP]
  region: [any]
  equipment: [any]
  voltage_level: [distribution, behind_the_meter]
  applies_when: "modeling existing WWTP electrical load profile as a baseline before the AI factory is added"
sources:
  - raw/wiki_legacy/regulations/wwtp_buffer_setback.md
related:
  - "[[wwtp_45mgd_archetype]]"
  - "[[src_legacy_wwtp_buffer_setback]]"
  - "[[service_transformer]]"
  - "[[behind_the_meter_siting]]"
approved_by: null
approved_date: null
supersedes: null
---

# Block: WWTP load

## What this block represents

The existing electrical load of the host WWTP — aeration blowers, pumping, ancillaries, headworks, biosolids handling, building HVAC. This is a **baseline** that the AI factory adds on top of, not a new load. The block's job is to capture how much of the existing service-transformer capacity is already committed before the AI factory is sited.

For the Blog 2 worked case (45 MGD archetype) the baseline peak is ~3,750 kW; this number is sensitive to plant treatment process, climate, biogas-CHP utilization, and operational practice.

## Key sizing variables

- **Treatment design flow (MGD)** — primary scaling variable. Larger plants have larger absolute load.
- **Aeration kWh per MG treated** — typical range 0.4–0.8 kWh/MG depending on aeration technology (fine-bubble diffused vs mechanical) and effluent quality target.
- **Peak load multiplier** — peak / average ratio. Aeration blowers cycle hard at peak diurnal load (mid-afternoon).
- **Pumping load** — primary, secondary, tertiary, sludge pumping; varies with site topography.
- **Ancillaries** — UV disinfection, filter backwash, building HVAC, lighting, control rooms.
- **Biogas-CHP offset** — sites with anaerobic digestion + CHP can offset 20–50% of grid demand.
- **Daily load profile shape** — aeration peaks 14:00–18:00 typically; falls 25–35% overnight.

## Upstream dependencies

- Process-design choice (activated sludge vs membrane bioreactor vs trickling filter) — drives aeration intensity.
- Site biogas / CHP infrastructure — affects net grid import.

## Downstream dependencies

- **[[service_transformer]]** block: existing transformer capacity is sized to historical WWTP peak. Adding AI factory load forces a sizing reassessment.
- **[[behind_the_meter_siting]]** concept: the WWTP load shape (diurnal + biogas-offset + etc.) is part of why the WWTP is a viable BTM host.

## Source notes that inform this block

- [[src_legacy_wwtp_buffer_setback]] — site geometry context (where load equipment can sit relative to PV array).
- [[wwtp_45mgd_archetype]] — entity-level synthesis with the 3,750 kW headline number.

## Candidate assumptions pending review

- **3,750 kW peak for 25–60 MGD plants** — Aspen-style heuristic from process intuition; not survey-validated.
- **Diurnal profile shape** — aeration peaks mid-afternoon, falls 25–35% overnight — typical-plant assumption that varies with influent flow pattern (which itself varies with neighborhood character).
- **Aeration kWh/MG = 0.5 default** — within the typical range but a real site can be 0.3 (efficient fine-bubble + biogas CHP) or 0.9 (older plant, minimal CHP).
- **Biogas-CHP offset zero by default** — many plants do have CHP; the model currently treats CHP as a future opportunity rather than a baseline assumption.
- **Climate sensitivity** — aeration intensity is loosely temperature-dependent; not modeled here.

## What would make this block authoritative / reviewed

- **Reviewed**: peak-load number cross-checked against either EPA EnergyStar Portfolio Manager data (median for 25–60 MGD plants) or a sample of real WWTPs (DC Water, EBMUD, Austin). Diurnal profile validated against at least one operator-provided 8,760-hour load file. Biogas-CHP offset modeled explicitly per plant rather than zeroed.
- **Authoritative**: WEF Manual of Practice cited directly for aeration intensity ranges; EPA EnergyStar Portfolio Manager median for the size band cited for the peak number; a site-survey paper cited for the diurnal shape.
