---
title: "Legacy note: Bifacial modules — yield gain"
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
  applies_when: "PV array sizing where module-level bifacial uplift is being modeled"
sources:
  - raw/wiki_legacy/pv/bifacial_gain.md
related:
  - "[[pv_array]]"
  - "[[src_legacy_single_axis_tracker]]"
  - "[[src_legacy_pv_lazard_lcoe_2024]]"
approved_by: null
approved_date: null
supersedes: null
---

# Legacy note — Bifacial modules: yield gain

## Source Summary

Internal PV note imported from `raw/wiki_legacy/pv/bifacial_gain.md`. Captures the typical bifacial-yield-gain numbers used in early-stage sizing, the dependence on ground albedo, and the interaction with tracking modality. Default value is +5 to +12% real-world yield over mono-facial at equal DC nameplate.

## Key Claims

- Bifacial gain over mono-facial at equal DC nameplate: **+5 to +12%** in real deployments.
- Sweet spot: single-axis tracker + GCR 0.35 ≈ +7% on average across US latitudes.
- CAPEX uplift vs mono-facial: +$0.04–0.08/W DC depending on module brand.
- Bifaciality coefficient (back-side/front-side efficiency ratio) for modern TOPCon/HJT: 70–80%.
- Albedo dependence:
  - Dry soil / mown grass: 0.15–0.20 → +3–5% gain
  - White gravel / light concrete: 0.30–0.40 → +7–9%
  - Snow: 0.70–0.90 → >+15% (only when snow-covered)
- Grass-covered WWTP buffer zones typically yield 5–8% gain — the default in `pv_tools.py`.
- Interaction with tracking:
  - Fixed-tilt + bifacial: +3–5%
  - Single-axis + bifacial: +6–8% (industry workhorse)
  - Dual-axis + bifacial: diminishing returns, dual-axis already captures most of it

## Engineering Use

- Bifacial-uplift number for any PV sizing tool default. Use 7% for grass-buffer WWTP sites (Blog 2 default).
- CAPEX uplift number ($0.04–0.08/W) for the sensitivity comparison vs mono-facial.
- Reasoning for why single-axis bifacial is the industry default: stacks multiplicatively with tracking.

## Limitations

- Albedo numbers vary with surface treatment, vegetation management, and seasonal change. The "5–8% for grass" number is a planning heuristic; real measurement requires site-specific reflectance data.
- Bifaciality coefficient varies by module manufacturer and technology. The 70–80% range is current 2024 TOPCon/HJT; older PERC modules are lower.
- Snow albedo is a very narrow operating regime and should not be relied on outside northern climates with sustained snow cover.
- Module-level pricing for bifacial vs mono-facial is in flux; 2024 numbers may not hold.
- This note paraphrases NREL TP-5K00-67198 and vendor datasheets; promotion to reviewed requires re-grounding against the NREL technical report directly and at least one site-measured case study.

## Related

- [[pv_array]] — flowsheet block where bifacial uplift is one of the sizing variables.
- [[src_legacy_single_axis_tracker]] — sibling source for the tracking modality the bifacial gain stacks with.
- [[src_legacy_pv_lazard_lcoe_2024]] — PV CAPEX context including bifacial premium.
- [[src_legacy_fixed_tilt]] — alternative configuration where bifacial has lower gain.

## Informs

- PV nameplate sizing: AC kWh/yr = DC kWp × specific yield × (1 + bifacial gain).
- CAPEX line: include bifacial premium where Lazard's bifacial-tracker number is being used.
- Site-design rule: keep array-to-ground albedo as high as practical (light gravel) to maximize bifacial gain.

## Source citations the legacy note relied on

- NREL Technical Report TP-5K00-67198 "Bifacial PV Performance".
- SolarEdge, Longi, Jinko bifacial product datasheets.
- PV Magazine bifacial tracker studies 2022–2024.
