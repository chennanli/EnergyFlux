---
title: "Block: DC bus"
authority: candidate
status: active
created: 2026-05-02
updated: 2026-05-02
informs: [dc_bus]
scope:
  host_type: [WWTP, chemical, substation, campus]
  region: [any]
  equipment: [GB200_NVL72, any]
  voltage_level: [behind_the_meter, distribution]
  applies_when: "DC distribution architecture inside a colocated AI inference site"
sources:
  - raw/wiki_legacy/capex/dc_industry_benchmarks.md
  - raw/wiki_legacy/hardware/blackwell_gb200_nvl72.md
related:
  - "[[ai_racks]]"
  - "[[inverter]]"
  - "[[bess]]"
  - "[[src_legacy_dc_industry_benchmarks]]"
  - "[[src_legacy_blackwell_gb200_nvl72]]"
approved_by: null
approved_date: null
supersedes: null
---

# Block: DC bus

## What this block represents

The DC distribution between the rectifier output (or DC-coupled PV/BESS) and the AI rack input. In a conventional AC-coupled architecture (the Blog 2 default) this is a short low-voltage DC stage internal to the rack — Blackwell GB200 NVL72 nominally runs an internal 800 V DC bus. In a DC-coupled architecture (forward-looking), the DC bus would extend to PV and BESS, eliminating the inverter stage and reclaiming several percentage points of round-trip efficiency.

The block is thin in Blog 2's default configuration but matters for two future moves: (1) DC-coupled PV/BESS, (2) HVDC distribution at MW-class sites.

## Key sizing variables

- **Bus voltage** — nominally 400–800 V DC inside the rack; 1,500 V DC for site-level DC-coupling.
- **Total DC IT load (MW)** — `rack_count × per_rack_facility_kW`. For Blog 2 45 MGD: 21 racks × 125 kW = 2.62 MW.
- **PUE multiplier** — facility load / IT load ratio; 1.15–1.25 for liquid-cooled Blackwell.
- **Headroom for cooling auxiliaries** — chilled-water pumps, CDU, rear-door HX fans count against the DC bus capacity.
- **Redundancy tier** — Tier III is the Blog 2 default; Tier IV adds 30–40% on capacity.

## Upstream dependencies

- **[[inverter]]** block (AC-coupled architecture): inverter AC output → step-down transformer → rectifier → DC bus.
- **[[pv_array]]** block (DC-coupled architecture, future): PV directly feeds DC bus through a DC-DC stage.
- **[[bess]]** block (DC-coupled architecture, future): BESS directly couples to DC bus.

## Downstream dependencies

- **[[ai_racks]]** block: receives DC power. Per-rack draw (~125 kW for GB200) drives total DC bus capacity.
- Facility cooling load: CDU pumps, chiller compressors, rear-door HX fans all draw DC for the cooling auxiliaries that keep the racks at temperature.

## Source notes that inform this block

- [[src_legacy_dc_industry_benchmarks]] — facility CAPEX numbers including DC distribution.
- [[src_legacy_blackwell_gb200_nvl72]] — per-rack DC draw and cooling architecture.

## Candidate assumptions pending review

- **AC-coupled default** — chosen because it's the industry standard and the worked Blog 2 case. DC-coupled is a real future option that this block does not currently model.
- **Bus voltage 400–800 V DC inside rack** — Blackwell-specific; future Vera Rubin-class platforms may push higher.
- **PUE 1.15–1.25** — for liquid cooling under benign ambient. Hot-climate (TX, AZ) sites may exceed this; the block currently uses a single planning value.
- **Tier III redundancy** — Blog 2 default; the choice has CAPEX and reliability implications a real project must justify.
- **Cooling-auxiliaries headroom** — currently bundled into the PUE multiplier; a real DC bus design separates IT load and aux load explicitly.

## What would make this block authoritative / reviewed

- **Reviewed**: sized against at least one realistic site one-line diagram (transformer secondary → rectifier → DC bus → racks); PUE assumption replaced with a measured value or modeled output for the climate zone; redundancy tier choice justified explicitly. DC-coupled vs AC-coupled trade-off documented as a separate decision page if the project is exploring it.
- **Authoritative**: NVIDIA reference DC architecture guide cited directly; ASHRAE thermal guidelines cited for the climate-PUE relationship.
