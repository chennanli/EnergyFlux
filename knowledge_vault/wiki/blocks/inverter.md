---
title: "Block: Inverter"
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
  applies_when: "PV inverter + BESS PCS sizing inside a BTM colocated AI inference site"
sources:
  - raw/wiki_legacy/pv/single_axis_tracker.md
  - raw/wiki_legacy/capex/pv_lazard_lcoe_2024.md
  - raw/wiki_legacy/capex/bess_nrel_atb_2024.md
related:
  - "[[pv_array]]"
  - "[[bess]]"
  - "[[dc_bus]]"
  - "[[src_legacy_pv_lazard_lcoe_2024]]"
  - "[[src_legacy_bess_nrel_atb_2024]]"
approved_by: null
approved_date: null
supersedes: null
---

# Block: Inverter

## What this block represents

The power-electronics interface between the PV array (DC) and the AC bus. In Blog 2's architecture this is a **central inverter** topology — typically several 500–1,500 kW units, each serving a sub-array — chosen for cost-per-watt over string inverters at utility scale.

A separate but related concept is the **BESS PCS** (power conversion system), which is the BESS-side inverter. This block page covers PV inverters; the BESS PCS is described in [[bess]].

## Key sizing variables

- **Inverter nameplate AC kW per unit** — Blog 2 default 550 kW central.
- **Inverter count** — `pv_kwp_dc / (per_unit_kw × ILR)`. For 7,474 kWp DC and ILR 1.25: 7,474 / (550 × 1.25) ≈ 11 units.
- **Inverter loading ratio (ILR)** — DC nameplate / AC capacity, default 1.25. Higher ILR (1.3–1.4) increases clipping loss but reduces inverter CAPEX per kW.
- **Inverter efficiency** — modern central units run ~98–99% peak.
- **Output voltage** — 480 V AC three-phase typical for central inverters; transformer steps up to medium voltage.

## Upstream dependencies

- **[[pv_array]]** block: provides DC input. Inverter count and ILR are derived from PV nameplate.
- DC string voltage and current ranges (set by module wattage, modules-per-string, strings-per-inverter — these are inverter-side product spec details, not site decisions).

## Downstream dependencies

- The site **AC collection bus** (typically 480 V → step-up transformer → 12.47 kV or 25 kV primary distribution).
- **[[service_transformer]]** block: the inverter's AC output joins WWTP load and BESS at the transformer secondary.
- **[[dc_bus]]** block: in a DC-coupled architecture (out of scope for Blog 2's AC-coupled default), inverter would be skipped on the PV side and a DC-DC stage would replace it.

## Source notes that inform this block

- [[src_legacy_pv_lazard_lcoe_2024]] — inverter is part of the per-W PV CAPEX number.
- [[src_legacy_single_axis_tracker]] — single-axis tracker layout drives inverter pad placement and string topology.
- [[src_legacy_bess_nrel_atb_2024]] — BESS PCS sizing and CAPEX is a separate but related inverter element.

## Downstream dependencies (continued)

- Anti-islanding / non-export logic in the inverter firmware: required for [[src_legacy_tx_ercot_interconnect]]'s "non-export PV" configuration to actually be enforced.

## Candidate assumptions pending review

- **Central inverter, 550 kW** — chosen as the round-number Blog 2 default. Real projects pick from a vendor catalog (SMA, Sungrow, Power Electronics, etc.); 540 / 600 / 1,500 kW are also common.
- **ILR 1.25** — industry default, but tariff-dependent. Sites optimizing for ITC capacity vs PTC energy will pick differently.
- **Inverter efficiency ~98%** — peak; real annual-average is 1–2 percentage points lower depending on load profile.
- **Anti-islanding / non-export logic** — a real design must specify the inverter firmware mode and verify with the utility; this block currently treats it as a feature flag, not a designed control loop.

## What would make this block authoritative / reviewed

- **Reviewed**: at least one vendor RFQ benchmarked against the assumed efficiency, ILR, and CAPEX numbers; a senior electrical engineer has reviewed the central-vs-string topology decision for a representative Blog 2 archetype site.
- **Authoritative**: inverter datasheets directly cited as authoritative source pages (SMA, Sungrow, Power Electronics, etc.). The path: promote one or two vendor datasheets to authoritative source pages; this block then cites them and is promoted to reviewed.
