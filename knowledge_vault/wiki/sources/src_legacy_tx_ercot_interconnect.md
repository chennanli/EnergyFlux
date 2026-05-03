---
title: "Legacy note: Texas / ERCOT interconnection for a BTM AI factory"
authority: legacy
status: active
created: 2026-05-02
updated: 2026-05-02
informs: [grid]
scope:
  host_type: [WWTP, chemical, substation, campus]
  region: [ERCOT]
  equipment: [any]
  voltage_level: [distribution, behind_the_meter]
  applies_when: "interconnection / service-upgrade planning for a BTM colocated AI inference site in ERCOT (TX)"
sources:
  - raw/wiki_legacy/regulations/tx_ercot_interconnect.md
related:
  - "[[service_transformer]]"
  - "[[behind_the_meter_siting]]"
approved_by: null
approved_date: null
supersedes: null
---

# Legacy note — ERCOT interconnection for BTM AI factories

## Source Summary

Internal regulatory brief imported from `raw/wiki_legacy/regulations/tx_ercot_interconnect.md`. Captures the rules around ERCOT interconnection thresholds, when a BTM project can avoid the formal ERCOT generator queue, and what utility-side work (Oncor / Centerpoint / AEP TX) is still required.

## Key Claims

- Conventional grid-scale projects: 3–7 year ERCOT interconnection queue.
- BTM projects under specific export / import thresholds: can energize in 6–12 months by avoiding the queue and doing only a facility-level Distribution Service Agreement.
- ERCOT key thresholds (Protocols 2024):
  - **Small Generator / 20 MW rule**: PV + BESS combined nameplate <20 MW, non-export → no formal generator interconnection.
  - **New load / 5 MW rule**: new retail load <5 MW at an existing metered service → typically a service upgrade with Level 2 planning study.
  - **5–20 MW load**: utility-specific Level 3 study, $50k–$150k, 6–9 months.
- Worked WWTP arrangement (5–8 MWp PV + 4 MW DC + 8 MWh BESS, all <20 MW total, non-export PV): stays in service-upgrade territory, avoids the long queue.
- Schedule killers that can still apply: utility transformer upgrade lead time (6–9 months, sometimes 18 months if utility is capacity-constrained); TCEQ environmental notice (~90 days); property easement negotiation.

## Engineering Use

- Justifies the "months not years" schedule claim in Blog 2 for ERCOT BTM sites — but ONLY for ERCOT and ONLY under the specific thresholds.
- Provides the threshold numbers that any project must verify (20 MW combined, 5 MW retail load, non-export configuration).
- Identifies the dominant remaining schedule risk: utility-side transformer procurement, not ERCOT process.

## Limitations

- **ERCOT-only.** These thresholds and process steps are scoped to ERCOT/Texas. Applying them in CAISO, PJM, MISO, NYISO, or ISO-NE is a scope mis-application — those markets have their own rules.
- "Non-export PV" interconnection requires the inverter / EMS configuration to actually curtail before pushing to grid; that's a real engineering constraint, not a paper one.
- Utility-territory specifics (Oncor vs Centerpoint vs AEP TX) can introduce additional Level 3 study requirements that the source does not detail.
- Transformer procurement times have been extending in 2024–2025 across the US; the 6–9 month figure may be optimistic.
- ERCOT Protocols update annually; the 2024 thresholds may shift.
- TCEQ environmental notice (~90 days) is for a typical case; environmental-justice census tracts add 90–180 days.
- This note paraphrases ERCOT Protocols, Oncor tariffs, and PUC-Texas rules. Promotion to reviewed requires re-grounding against ERCOT Protocols Section 16 directly and verifying with current utility tariff schedules.

## Related

- [[service_transformer]] — the flowsheet block whose upgrade is the dominant schedule item.
- [[behind_the_meter_siting]] — the concept page that uses this regulatory regime as part of the "months vs years" argument.

## Informs

- Schedule narrative in any ERCOT BTM proposal: "months, not years" with the 6–12 month service-upgrade caveat and the transformer-lead-time risk.
- Sizing-stage non-export PV constraint: the inverter / EMS must demonstrate it stays under the 20 MW threshold and never exports.
- Project boundary check: total combined nameplate (PV + BESS + DC) must stay <20 MW for the small-generator path; total retail load <5 MW for the simpler service-upgrade path.

## Source citations the legacy note relied on

- ERCOT Protocols Section 16 (Resource Interconnection), 2024 edition.
- Oncor Electric Delivery Company Tariff — Schedule Q, Primary/Secondary Service.
- Public Utility Commission of Texas Substantive Rules §25.211 (Interconnection of DG).
