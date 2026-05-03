---
title: "Legacy note: PV CAPEX — Lazard LCOE+ 2024 reference"
authority: legacy
status: active
created: 2026-05-02
updated: 2026-05-02
informs: [pv]
scope:
  host_type: [WWTP, any]
  region: [any]
  equipment: [any]
  voltage_level: [distribution, behind_the_meter, transmission]
  applies_when: "early-stage utility-scale or BTM PV CAPEX and LCOE modeling, 2024 vintage"
sources:
  - raw/wiki_legacy/capex/pv_lazard_lcoe_2024.md
related:
  - "[[pv_array]]"
  - "[[src_legacy_single_axis_tracker]]"
  - "[[src_legacy_bifacial_gain]]"
approved_by: null
approved_date: null
supersedes: null
---

# Legacy note — PV CAPEX (Lazard LCOE+ 2024)

## Source Summary

Internal cost brief imported from `raw/wiki_legacy/capex/pv_lazard_lcoe_2024.md`. Summarizes Lazard LCOE+ 2024 numbers for utility-scale ground-mount PV, turnkey installed cost (modules + inverters + trackers + BoS + engineering + land prep). Excludes land acquisition, interconnection studies, and financing.

## Key Claims

- Installed CAPEX, 2024 USD (DC nameplate):
  - Fixed-tilt mono-facial: $0.80–0.95/W
  - Single-axis tracker: $0.90–1.05/W
  - Single-axis bifacial: $0.95–1.10/W
- LCOE (unsubsidized):
  - Fixed-tilt mono-facial: $28–38/MWh
  - Single-axis tracker: $26–36/MWh
  - Single-axis bifacial: $24–34/MWh
- For a 5–10 MW BTM project, the upper end of each range applies (small-project + inflation adder).
- Includes: modules, inverters, trackers, racking, foundations, DC + AC wiring, SCADA, transformers up to metering, EPC labor, commissioning, permits.
- Excludes: land acquisition (typically $0 for a WWTP buffer in-kind lease), utility interconnection study + upgrade ($50k–$300k), environmental review ($20k–$100k), project financing.
- Blog 2 default (5.7 MWp single-axis bifacial): CAPEX midpoint $6.0M; LCOE midpoint $29/MWh unsubsidized.

## Engineering Use

- Provides the CAPEX/W and LCOE numbers for any PV pro-forma at design stage.
- Anchors the [[pv_array]] flowsheet block and informs tracker / bifacial selection economics.
- Confirms why single-axis bifacial is the default for utility-scale: best LCOE in the table at 25°–45°N latitude.

## Limitations

- 2024 USD; PV CAPEX is moving (downward overall, but with tariff and supply-chain disruption in some quarters). Promotion to reviewed requires year-current numbers.
- LCOE depends on assumed financing structure (Lazard uses a specific WACC); for a BTM colocated case the right LCOE may be higher or lower depending on project finance.
- Lazard explicitly excludes dual-axis from utility-scale tables on cost grounds — meaning the dual-axis comparison number used elsewhere is from a different source.
- This note is paraphrased; promotion to reviewed requires re-grounding against the Lazard report directly and comparing to NREL ATB for the same year.

## Related

- [[pv_array]] — flowsheet block for the PV array.
- [[src_legacy_single_axis_tracker]] — sibling source on the default tracker choice.
- [[src_legacy_bifacial_gain]] — sibling source on the bifacial yield gain.
- [[src_legacy_fixed_tilt]] — sibling source on the conservative-floor PV configuration.
- [[src_legacy_dual_axis]] — sibling source on the niche dual-axis option.

## Informs

- PV CAPEX line in any sizing pro-forma.
- LCOE comparison when evaluating PV against grid-only or PV+BESS options.
- Tracker-vs-fixed-tilt sensitivity analysis.

## Source citations the legacy note relied on

- Lazard's Levelized Cost of Energy+ 2024 Report (lazard.com/perspective/lcoeplus-june-2024).
- NREL Annual Technology Baseline 2024, utility-scale PV tab.
- SEIA / Wood Mackenzie US Solar Market Insight, Q4 2024.
