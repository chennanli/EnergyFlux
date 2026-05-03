---
title: "Legacy note: BESS CAPEX — NREL Annual Technology Baseline 2024"
authority: legacy
status: active
created: 2026-05-02
updated: 2026-05-02
informs: [bess]
scope:
  host_type: [WWTP, any]
  region: [any]
  equipment: [LFP_BESS]
  voltage_level: [distribution, behind_the_meter, transmission]
  applies_when: "early-stage BESS CAPEX modeling for utility-scale or BTM Li-ion LFP, 4-hour duration"
sources:
  - raw/wiki_legacy/capex/bess_nrel_atb_2024.md
related:
  - "[[bess_4hr_lfp]]"
  - "[[bess]]"
  - "[[src_legacy_4h_battery_standard]]"
approved_by: null
approved_date: null
supersedes: null
---

# Legacy note — BESS CAPEX (NREL ATB 2024)

## Source Summary

Internal cost brief imported from `raw/wiki_legacy/capex/bess_nrel_atb_2024.md`. Summarizes NREL Annual Technology Baseline 2024 numbers for grid-scale Li-ion LFP, 4-hour duration, turnkey installed cost at the facility battery DC bus. Components include cells, BMS, PCS, thermal management, enclosure, EPC labor, commissioning. Land and substation upgrade are out of scope.

## Key Claims

- Total installed CAPEX, 4-hour LFP, 2024 USD: **$230–320/kWh**, ATB midpoint **$275/kWh**.
- Component breakdown:
  - Cells (LFP): $95–125/kWh
  - Inverter (PCS) + controls: $55–80/kWh
  - Thermal management + fire suppression: $25–40/kWh
  - EPC + BoS + commissioning: $55–75/kWh
- Duration scaling (CAPEX scales non-linearly with duration; inverter is fixed per MW, cells scale per MWh):
  - 2-hour: ~$450/kWh (high inverter share)
  - 4-hour: ~$275/kWh (sweet spot)
  - 6-hour: ~$210/kWh
  - 8-hour: ~$180/kWh
- Augmentation: ~$40/kWh at year 10 (replacing ~20% of cells); amortized adds ~$5–8/kWh over 20 years.
- Blog 2 default (8 MWh, 4-hour): nameplate $2.2M, $2.5M total lifecycle including augmentation reserve.

## Engineering Use

- Provides the CAPEX line for any BESS sizing / pro-forma at design stage.
- Confirms why 4-hour is the cost sweet spot (cells dominate at long duration; inverter dominates at short duration; 4-hour is where the curves cross).
- Augmentation reserve number ($5–8/kWh amortized) is the input to lifecycle-cost modeling.

## Limitations

- 2024 USD; will go stale after the 2025 and 2026 NREL ATB cycles. Promotion to reviewed requires re-pulling from `atb.nrel.gov` for the relevant year.
- Numbers are utility-scale midpoints; small (<5 MWh) or behind-the-meter projects often run 15–30% above these for fixed-cost reasons (smaller PCS amortizes worse, EPC mobilization not amortized, etc.).
- Excludes interconnection, land, and substation upgrades — those can dominate total project cost at small scale.
- LFP-specific. NMC chemistry has different cost trajectory and different fire-code/safety considerations.
- This note is a paraphrase of NREL ATB; promotion to reviewed requires re-grounding against the ATB worksheet directly and verifying which scenario (Conservative / Moderate / Advanced) was used.

## Related

- [[bess_4hr_lfp]] — entity page where these CAPEX numbers anchor the cost narrative.
- [[src_legacy_4h_battery_standard]] — sibling source on duration choice.
- [[src_legacy_tou_arbitrage]] — sibling source on revenue side.
- [[bess]] — flowsheet block.

## Informs

- Pro-forma CAPEX line for BESS at any sizing stage.
- Duration tradeoff economics in any BESS-duration sensitivity study.
- Augmentation reserve in any 20-year lifecycle cost model.

## Source citations the legacy note relied on

- NREL Annual Technology Baseline 2024, Utility-Scale Battery Storage tab (atb.nrel.gov/electricity/2024/utility-scale_battery_storage).
- Lazard's Levelized Cost of Storage+ 2024 (LCOS+).
- DOE Energy Storage Grand Challenge roadmap, 2023.
