# WWTP buffer zones — what the setback rules actually say

Every US WWTP maintains a **buffer zone** around its operational tanks. This is the key resource for siting a colocated AI inference facility: the land is already owned, already zoned, already permitted, and deliberately empty.

## Federal baseline: 40 CFR Part 503

EPA 40 CFR §503 (biosolids use and disposal) imposes surface disposal setbacks, but not a general operational buffer for treatment tanks themselves. The real operational buffer rules come from **state** health / environmental departments.

## Typical state requirements

* **California (Title 22)**: 100 ft (30 m) from any treatment unit to the property boundary. 500 ft from aerosol-generating processes (aerated ponds) to habitable buildings.
* **Texas (TCEQ Chapter 217)**: 150 ft from digesters + aeration basins to the property line. No specific rule for PV arrays within the buffer — interpreted as permissible.
* **Florida (FDEP)**: 100 ft from operational units to residential buildings; 50 ft to commercial.
* **New York (6 NYCRR 750)**: 100 ft from operational units to offsite property; 200 ft to residential.

## What this means for PV siting

The buffer is **between the treatment tanks and the property boundary**. PV arrays can generally occupy this buffer as long as:

1. Modules are at least 50 ft from aeration basins (H₂S corrosion, microbial aerosols).
2. Racking heights don't interfere with sludge-hauling access roads.
3. Arrays don't block lighting / CCTV sightlines required by the operator's security plan.

Practical consequence: **of ~20 acres buffer at a 30 MGD plant, 17–18 acres are PV-viable**. That's the 0.90 "land fraction" constant in `sizing.py`.

## What stops a project

* **H₂S corrosion risk** near primary clarifiers — keep a 30 m corrosion exclusion zone around primary aeration.
* **Flood-zone restrictions** — many WWTPs are intentionally sited in floodplain. FEMA rules may restrict substation equipment below BFE+2 ft.
* **Environmental Justice zones** — recent EPA guidance (Aug 2024) requires enhanced community notification for industrial co-location in EJ census tracts. Doesn't block, but adds 90–180 days to permitting.

## Sources

* 40 CFR §503 (federal biosolids).
* California Title 22, Division 4, Chapter 3, §64435.
* Texas Administrative Code Title 30, Part 1, Chapter 217.
* WEF Manual of Practice No. 8, "Design of Municipal Wastewater Treatment Plants" (6th ed), 2018.
