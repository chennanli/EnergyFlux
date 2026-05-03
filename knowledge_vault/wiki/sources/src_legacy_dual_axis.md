---
title: "Legacy note: Dual-axis tracking PV"
authority: legacy
status: active
created: 2026-05-02
updated: 2026-05-02
informs: [pv]
scope:
  host_type: [any]
  region: [any]
  equipment: [any]
  voltage_level: [distribution, transmission]
  applies_when: "PV configuration choice when peak yield matters more than CAPEX or where latitudes >50°N apply"
sources:
  - raw/wiki_legacy/pv/dual_axis.md
related:
  - "[[pv_array]]"
  - "[[src_legacy_single_axis_tracker]]"
  - "[[src_legacy_pv_lazard_lcoe_2024]]"
approved_by: null
approved_date: null
supersedes: null
---

# Legacy note — Dual-axis tracking PV

## Source Summary

Internal PV note imported from `raw/wiki_legacy/pv/dual_axis.md`. Two-axis trackers follow the sun in both azimuth and elevation; the note captures why this configuration almost never wins for utility-scale ground-mount in the continental US, and the niche cases where it does.

## Key Claims

- Land density: ~180 kWp DC per acre at GCR 0.25. Lower than single-axis or fixed because dual-axis trackers need wider row-to-row spacing to avoid mutual shading.
- Specific yield: +5% over single-axis bifacial in best cases. In central US (~33°N), dual-axis sometimes underperforms single-axis bifacial because the narrower aperture + tracker tilt reduces back-side light collection.
- CAPEX uplift: +20–30% over single-axis, driven by the second-axis drive mechanism and O&M complexity.
- Reliability: ~98% uptime vs 99%+ for single-axis. More moving parts, more gearbox failures.
- When it wins: very-high-value sites (island grids, military, research), high-latitude sites (>50°N), CPV.
- LCOE math against it for typical US ground-mount: +5% yield × $1.10/W is smaller dollar/MWh than the +$0.20/W CAPEX uplift dual-axis imposes.

## Engineering Use

- Provides the empirical "do not pick dual-axis for utility-scale US ground-mount" decision rule with the supporting LCOE math.
- Provides the niche-case list for when dual-axis is justified.
- Land density (180 kWp/acre at GCR 0.25) for any planning-stage feasibility calculation.

## Limitations

- The LCOE-against-it math uses 2024 single-axis CAPEX numbers; if dual-axis CAPEX comes down enough or if module prices spike, the conclusion could flip.
- "Almost never wins for US utility-scale" is an LCOE-driven statement; cases where capacity factor matters more than $/MWh (small island grids, EV charging hubs) can flip the decision.
- High-latitude (>50°N) cases are not a US continental concern but are relevant for Alaska or international sites.
- The reliability gap (98% vs 99%+) is from trade press reporting, not a primary reliability study.
- This note paraphrases NREL PVWatts runs, SolarEdge/Soltec datasheets, and Lazard's exclusion of dual-axis from utility-scale tables. Promotion to reviewed requires re-grounding against any one of those primary sources.

## Related

- [[pv_array]] — flowsheet block where this is the dominated option.
- [[src_legacy_single_axis_tracker]] — the configuration this note explains why dual-axis loses to.
- [[src_legacy_pv_lazard_lcoe_2024]] — CAPEX/LCOE context.

## Informs

- Default PV configuration choice: do not pick dual-axis for utility-scale US ground-mount.
- LCOE comparison narrative: dual-axis is the dominated option in almost every modern US ground-mount analysis.
- Niche-case identification: only justify dual-axis when explicitly outside the standard continental-US ground-mount regime.

## Source citations the legacy note relied on

- NREL PVWatts v8 dual-axis benchmark runs, 2024.
- SolarEdge + Soltec trade press on dual-axis product lines, 2023.
- Lazard LCOE+ 2024 — Lazard explicitly excludes dual-axis from utility-scale comparative tables on cost grounds.
