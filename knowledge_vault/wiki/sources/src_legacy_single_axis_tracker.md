---
title: "Legacy note: Single-axis tracking PV"
authority: legacy
status: active
created: 2026-05-02
updated: 2026-05-02
informs: [pv]
scope:
  host_type: [any]
  region: [any]
  equipment: [any]
  voltage_level: [distribution, behind_the_meter, transmission]
  applies_when: "PV configuration choice for utility-scale ground-mount in 25°–45°N latitude band"
sources:
  - raw/wiki_legacy/pv/single_axis_tracker.md
related:
  - "[[pv_array]]"
  - "[[src_legacy_bifacial_gain]]"
  - "[[src_legacy_fixed_tilt]]"
  - "[[src_legacy_pv_lazard_lcoe_2024]]"
approved_by: null
approved_date: null
supersedes: null
---

# Legacy note — Single-axis tracking PV

## Source Summary

Internal PV note imported from `raw/wiki_legacy/pv/single_axis_tracker.md`. The default choice for utility-scale ground-mount in the US. Single-axis horizontal trackers rotate modules east-to-west on one axis to follow the sun, producing roughly 15–20% higher annual yield than fixed tilt at modest CAPEX premium.

## Key Claims

- Land density: ~325 kWp DC per acre at GCR 0.35.
- Specific yield (AC, after derate): +18% over fixed tilt, zone-dependent. At 30°N ≈ 1,830 kWh/kWp/yr; at 40°N ≈ 1,600 kWh/kWp/yr.
- CAPEX uplift: +$0.05–0.10/W DC vs fixed tilt — about 6–10% premium on total project cost.
- Reliability: modern trackers ship with >99% uptime over 20 years; gear backlash is the main failure mode. Design life 25 years.
- Wins nearly always for sites >1 MW in 25°–45°N band — beats fixed-tilt on LCOE in almost every modern US ground-mount analysis.
- Loses for: severe slopes (>15%), heavy tree shading, narrow irregular parcels, sites north of 50°N.
- Stacks with bifacial: +18% (tracking) + 7% (bifacial) ≈ +25% over fixed-tilt mono-facial. Single-axis bifacial is the industry default.

## Engineering Use

- Default PV configuration for any WWTP buffer site in the 25°–45°N band — Blog 2's worked-case archetype assumption.
- Land density (325 kWp/acre at GCR 0.35) is the planning heuristic for parcel-fit calculations.
- The +18% (tracking) + 7% (bifacial) ≈ +25% formula is the headline yield-vs-fixed-tilt math.

## Limitations

- The "+18% over fixed tilt" specific-yield gain is zone-dependent; at higher latitudes the gain shrinks. North of 50°N the tracking gain is small enough that fixed-tilt is competitive.
- 1,830 kWh/kWp/yr at 30°N and 1,600 kWh/kWp/yr at 40°N are typical-meteorological-year averages; real years vary ±10% with cloud cover, soiling, and inverter degradation.
- Tracker reliability claim (>99% uptime) is a manufacturer statement; field-measured performance after 10+ years can be lower depending on O&M practice.
- CAPEX uplift of $0.05–0.10/W DC vs fixed-tilt is from 2024 numbers; the gap is shrinking as tracker manufacturing scales.
- This note paraphrases NREL ATB, Lazard LCOE+, and tracker-vendor datasheets. Promotion to reviewed requires either NREL ATB re-grounding or vendor RFQ.

## Related

- [[pv_array]] — flowsheet block where this is the default configuration.
- [[src_legacy_bifacial_gain]] — the gain that stacks multiplicatively with tracking.
- [[src_legacy_fixed_tilt]] — the alternative configuration this beats on LCOE.
- [[src_legacy_dual_axis]] — niche alternative.
- [[src_legacy_pv_lazard_lcoe_2024]] — CAPEX/LCOE context.

## Informs

- Default PV configuration in Blog 2 worked case: single-axis bifacial.
- Land density planning heuristic: 325 kWp/acre at GCR 0.35 for the parcel-fit math.
- Annual energy estimate: kWp × specific_yield × (1 + bifacial_gain).
- LCOE comparison vs fixed-tilt: usually +6–10% CAPEX, +18% energy = significantly better LCOE.

## Source citations the legacy note relied on

- NREL Annual Technology Baseline 2024 (PV chapter).
- Lazard's Levelized Cost of Energy+ 2024, utility-scale ground-mount section.
- Array Technologies and NEXTracker datasheets, 2024.
