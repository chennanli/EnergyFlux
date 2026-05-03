---
title: "Legacy note: WWTP buffer zones — setback rules"
authority: legacy
status: active
created: 2026-05-02
updated: 2026-05-02
informs: [wwtp]
scope:
  host_type: [WWTP]
  region: [CAISO, ERCOT, PJM, NYISO, ISO-NE, any]
  equipment: [any]
  voltage_level: [distribution, behind_the_meter]
  applies_when: "PV-array siting and access planning inside a municipal WWTP buffer zone"
sources:
  - raw/wiki_legacy/regulations/wwtp_buffer_setback.md
related:
  - "[[wwtp_load]]"
  - "[[pv_array]]"
  - "[[behind_the_meter_siting]]"
  - "[[wwtp_45mgd_archetype]]"
approved_by: null
approved_date: null
supersedes: null
---

# Legacy note — WWTP buffer zones / setback rules

## Source Summary

Internal regulatory brief imported from `raw/wiki_legacy/regulations/wwtp_buffer_setback.md`. Captures the federal baseline (40 CFR §503), state-specific operational setbacks, and the practical constraints on PV array siting inside the buffer zone of a US municipal WWTP.

## Key Claims

- Federal baseline (40 CFR §503): biosolids surface-disposal setbacks; does not impose a general operational buffer for treatment tanks. Operational buffers come from state health/environmental departments.
- State requirements (typical):
  - **California (Title 22)**: 100 ft from any treatment unit to property boundary; 500 ft from aerated ponds to habitable buildings.
  - **Texas (TCEQ Chapter 217)**: 150 ft from digesters + aeration basins to property line; PV arrays within the buffer interpreted as permissible.
  - **Florida (FDEP)**: 100 ft to residential; 50 ft to commercial.
  - **New York (6 NYCRR 750)**: 100 ft to offsite property; 200 ft to residential.
- Practical PV-siting constraints:
  - Modules at least 50 ft from aeration basins (H₂S corrosion, microbial aerosols).
  - Racking must not interfere with sludge-hauling access roads.
  - Arrays must not block lighting / CCTV sightlines required by operator security.
- Heuristic: of ~20 acres buffer at a 30 MGD plant, 17–18 acres are PV-viable (~0.90 land fraction, the constant in `sizing.py`).
- Project killers: H₂S corrosion zone (30 m exclusion around primary aeration); FEMA flood-zone (BFE+2 ft restriction on substation equipment); EJ census tract enhanced notification (~90–180 days).

## Engineering Use

- Land fraction (0.90) for converting buffer-zone acres → PV-viable acres in early-stage sizing.
- State-by-state setback rule lookup for any specific WWTP siting decision.
- H₂S corrosion exclusion zone (30 m) as a hard constraint on PV layout.
- FEMA flood-zone elevation rule for substation siting.
- EJ schedule risk: 90–180 days additional permitting for sites in EJ census tracts.

## Limitations

- The "5 state" sample (CA / TX / FL / NY plus federal) is illustrative, not exhaustive — every state has its own rules. Promotion to reviewed requires checking the specific state for any specific project.
- TCEQ Chapter 217's interpretation that "PV arrays within the buffer are permissible" is the source's reading; for a real Texas project this should be confirmed in writing with TCEQ.
- The 0.90 land-fraction heuristic is a planning estimate, not a measured value at any specific site. Some sites have higher fractions (sparse infrastructure); some have lower (dense access roads, CHP equipment, biosolids handling).
- Federal EJ guidance has shifted under different administrations; the 90–180 day estimate is from Aug 2024 EPA guidance and is volatile.
- This note paraphrases 40 CFR §503, state codes, and WEF MOP 8 (a design manual). Promotion to reviewed requires either direct CFR/state-code verification or an attorney letter.

## Related

- [[wwtp_load]] — flowsheet block where the WWTP itself is modeled.
- [[pv_array]] — flowsheet block whose siting is constrained by these setbacks.
- [[wwtp_45mgd_archetype]] — entity page that uses the 0.90 land-fraction assumption.
- [[behind_the_meter_siting]] — the concept page where buffer-zone availability is one of the three required resources.

## Informs

- PV-viable acres calculation: viable_acres = buffer_acres × 0.90 (default).
- H₂S exclusion zone: 30 m around primary aeration.
- FEMA + EJ schedule and elevation constraints in any project plan.
- State-specific setback compliance for the four states explicitly captured.

## Source citations the legacy note relied on

- 40 CFR §503 (federal biosolids).
- California Title 22, Division 4, Chapter 3, §64435.
- Texas Administrative Code Title 30, Part 1, Chapter 217.
- WEF Manual of Practice No. 8, "Design of Municipal Wastewater Treatment Plants" (6th ed), 2018.
