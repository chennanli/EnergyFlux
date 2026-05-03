---
title: "Block: PV array"
authority: candidate
status: active
created: 2026-05-02
updated: 2026-05-02
informs: [pv]
scope:
  host_type: [WWTP, chemical, substation, campus]
  region: [any]
  equipment: [any]
  voltage_level: [distribution, behind_the_meter]
  applies_when: "PV array sizing inside an industrial-host BTM site"
sources:
  - raw/wiki_legacy/pv/single_axis_tracker.md
  - raw/wiki_legacy/pv/bifacial_gain.md
  - raw/wiki_legacy/pv/fixed_tilt.md
  - raw/wiki_legacy/pv/dual_axis.md
  - raw/wiki_legacy/capex/pv_lazard_lcoe_2024.md
related:
  - "[[src_legacy_single_axis_tracker]]"
  - "[[src_legacy_bifacial_gain]]"
  - "[[src_legacy_fixed_tilt]]"
  - "[[src_legacy_dual_axis]]"
  - "[[src_legacy_pv_lazard_lcoe_2024]]"
  - "[[inverter]]"
  - "[[dc_bus]]"
approved_by: null
approved_date: null
supersedes: null
---

# Block: PV array

## What this block represents

The on-site PV array that converts buffer-zone or rooftop sunlight into DC power for the colocated AI factory. In the EnergyFlux flowsheet this is the upstream-most generation block; everything else (inverter, BESS, DC bus, racks) sits downstream of its DC output.

For WWTP buffer sites the default configuration is **single-axis tracking + bifacial TOPCon modules** at GCR 0.35 — the industry-default trade between yield gain, land density, and CAPEX.

## Key sizing variables

- **DC nameplate (kWp)** — set by `pv_kwp = pv_viable_acres × land_density_kwp_per_acre`. Default land density 325 kWp/acre at GCR 0.35 ([[src_legacy_single_axis_tracker]]).
- **Tracking modality** — single-axis (default) / fixed-tilt (small or sloped sites) / dual-axis (rare). See [[src_legacy_dual_axis]] for why dual rarely wins.
- **Bifacial gain** — multiplicative uplift on yield, ~7% on grass-buffer WWTP ground ([[src_legacy_bifacial_gain]]).
- **Module wattage** — 580 W TOPCon is the Blog 2 default; affects module count but not nameplate.
- **Specific yield (kWh/kWp/yr)** — latitude-dependent; ~1,830 at 30°N, ~1,600 at 40°N ([[src_legacy_single_axis_tracker]]).
- **Performance ratio** — derate factor for soiling, mismatch, inverter clipping; default ~0.82 in `pv_tools.py`.
- **Inverter loading ratio (ILR)** — DC nameplate divided by AC inverter capacity; default 1.25.

## Upstream dependencies

- Available **buffer-zone acres** ([[src_legacy_wwtp_buffer_setback]]). For a WWTP buffer this is `total_buffer_acres × 0.90` after setbacks and access roads.
- Site latitude (drives specific yield).
- Albedo of the surface under the array (drives bifacial gain).

## Downstream dependencies

- **[[inverter]]** block: receives the DC string output and converts to AC. Inverter sizing is set by ILR against PV nameplate.
- **[[dc_bus]]** block: a DC-coupled architecture would route PV directly to the DC bus (skipping AC) — out of scope for this Blog 2 archetype but flagged as a future option.
- Grid-export limit: in non-export configurations ([[src_legacy_tx_ercot_interconnect]]) the inverter must curtail PV before pushing to grid.

## Source notes that inform this block

- [[src_legacy_single_axis_tracker]] — default tracking modality; +18% over fixed-tilt.
- [[src_legacy_bifacial_gain]] — default bifacial uplift; ~7% on grass.
- [[src_legacy_fixed_tilt]] — alternative configuration; the conservative-floor case.
- [[src_legacy_dual_axis]] — niche alternative; almost never picked in continental US.
- [[src_legacy_pv_lazard_lcoe_2024]] — CAPEX/LCOE numbers per configuration.

## Candidate assumptions pending review

The following are working assumptions in the current vault. None has been promoted to **reviewed** yet:

- **Land density 325 kWp/acre at GCR 0.35** — needs to be cross-checked against at least one real WWTP PV layout (e.g., Oakland EBMUD, Austin Walnut Creek, DC Water).
- **Bifacial gain 7% on grass** — needs site-measured albedo data, not a planning-stage heuristic, before promotion.
- **Performance ratio 0.82** — module + inverter + soiling + mismatch derate stack; needs validation against PVsyst run for at least one Blog 2 archetype site.
- **Inverter loading ratio 1.25** — industry-typical, but the right ILR depends on tariff structure (ITC vs PTC, capacity-credit rules); needs ground-truth against either.
- **Yield numbers (1,830 kWh/kWp/yr at 30°N, 1,600 at 40°N)** — TMY3 averages; would benefit from explicit TMY3 weather-file run for at least the Blog 2 worked case.

## What would make this block authoritative / reviewed

- **Reviewed**: the source notes are re-grounded against their primary sources (NREL ATB worksheet directly, Lazard LCOE+ report directly, vendor datasheet directly), AND a senior PE has signed off on the sizing rules used here. Each assumption above gets either a citation or a "rule of thumb pending validation" tag.
- **Authoritative**: not currently feasible at the block level — Authoritative status is reserved for primary external sources (NREL, NVIDIA, etc.), not for synthesis pages. The path is: promote individual source notes to authoritative; promote this block page to reviewed once it cites them.
