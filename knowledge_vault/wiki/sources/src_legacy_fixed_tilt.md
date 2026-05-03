---
title: "Legacy note: Fixed-tilt ground-mount PV"
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
  applies_when: "PV configuration choice for narrow / sloped / small parcels, or as a conservative-floor feasibility baseline"
sources:
  - raw/wiki_legacy/pv/fixed_tilt.md
related:
  - "[[pv_array]]"
  - "[[src_legacy_single_axis_tracker]]"
  - "[[src_legacy_pv_lazard_lcoe_2024]]"
approved_by: null
approved_date: null
supersedes: null
---

# Legacy note — Fixed-tilt ground-mount PV

## Source Summary

Internal PV note imported from `raw/wiki_legacy/pv/fixed_tilt.md`. The simplest PV configuration: modules on fixed steel frames angled near the site's latitude. No moving parts. The conservative floor for any feasibility narrative.

## Key Claims

- Land density: ~290 kWp DC per acre at GCR 0.40.
- Specific yield: reference baseline; all other tracking options report ratios relative to this.
- CAPEX: cheapest per-watt installed configuration, often $0.80–0.95/W DC turnkey.
- Reliability: highest — no moving parts; 25-year design life, <0.5% annual degradation.
- Wins for: narrow / irregular / steeply sloped parcels; rooftops; very small projects (<500 kWp); sites where O&M access is expensive.
- Loses for: open flat parcels >1 MW in continental US, where single-axis tracking beats it on LCOE.
- Why include in Blog 2: feasibility floor — a site that pencils on fixed-tilt always pencils on tracking.

## Engineering Use

- Conservative-floor narrative anchor for any feasibility study: "if the project pencils at fixed-tilt yield, it will only get better with tracking."
- Land density (290 kWp/acre) is the upper bound for available PV nameplate per acre — useful for early-stage parcel-fit screening.
- Cost-floor reference: the cheapest per-watt PV configuration that is grid-quality.

## Limitations

- Land density of 290 kWp/acre at GCR 0.40 is a planning heuristic; site-specific shading, slope, and access requirements often push real density 10–20% lower.
- Specific yield is the "reference baseline" only inside the source's narrative; the absolute kWh/kWp/yr depends on latitude, weather, soiling, etc.
- Reliability claim (<0.5%/yr degradation) is module-level; system-level losses from inverter, soiling, tracker downtime, etc., are larger.
- 2024 CAPEX numbers; PV module pricing is volatile.
- This note paraphrases NREL ATB and EnergySage commercial PV CAPEX surveys; promotion to reviewed requires re-grounding against either directly.

## Related

- [[pv_array]] — flowsheet block where this is one of three configuration options.
- [[src_legacy_single_axis_tracker]] — the alternative that wins on LCOE for >1 MW open parcels.
- [[src_legacy_dual_axis]] — the niche alternative for very high-value sites.
- [[src_legacy_pv_lazard_lcoe_2024]] — CAPEX/LCOE context.

## Informs

- Decision rule: pick fixed-tilt when (a) parcel is narrow/sloped/irregular, (b) project is <500 kWp, or (c) feasibility floor is the desired narrative.
- Pro-forma CAPEX line at the conservative end.
- Land-fit screening upper bound (kWp per acre).

## Source citations the legacy note relied on

- NREL Annual Technology Baseline 2024 (PV, fixed-tilt).
- EnergySage residential + commercial PV CAPEX reports, 2024.
