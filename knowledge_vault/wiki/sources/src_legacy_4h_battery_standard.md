---
title: "Legacy note: 4-hour battery as industry default (BESS)"
authority: legacy
status: active
created: 2026-05-02
updated: 2026-05-02
informs: [bess]
scope:
  host_type: [WWTP, any]
  region: [CAISO, ERCOT, any]
  equipment: [LFP_BESS]
  voltage_level: [distribution, behind_the_meter]
  applies_when: "design or sizing of utility-scale or BTM Li-ion BESS"
sources:
  - raw/wiki_legacy/bess/4h_battery_standard.md
related:
  - "[[bess_4hr_lfp]]"
  - "[[bess]]"
  - "[[src_legacy_bess_nrel_atb_2024]]"
approved_by: null
approved_date: null
supersedes: null
---

# Legacy note — 4-hour battery as industry default

## Source Summary

Internal design note imported from `raw/wiki_legacy/bess/4h_battery_standard.md`. Captures the rationale for why 4-hour Li-ion (LFP) is the de facto industry default for utility-scale and BTM BESS in the 2024–2026 US market, with the supporting numbers and citations the author was working from at the time.

## Key Claims

- Three forces converge on the 4-hour duration:
  1. **Capacity-credit accreditation**: CAISO and ERCOT both grant ~100% capacity credit to 4-hour batteries; 2-hour gets ~60%.
  2. **TOU evening-peak coverage**: most CA/TX/AZ TOU tariffs define on-peak as 4 PM–9 PM (5 hours); a 4-hour battery charged to 85% SOC by 4 PM carries most of the window.
  3. **Fire-code / energy-density envelope**: a 4-hour Li-ion BESS at ~2 MWh fits a standard 20-ft container with NFPA 855-compliant separation.
- Headline numbers cited by the source:
  - Standard duration: 4 hours at nameplate discharge
  - Round-trip efficiency: ~92% LFP
  - Cycle life: ~6,000 cycles at 80% DoD
  - Installed CAPEX (4-hour, utility-scale, 2024–2025): ~$230–320/kWh
  - Capacity fade: ~2.5%/yr, offset by replacing ~20% of cells at year 10

## Engineering Use

- Justifies the 4-hour duration as the BESS default for any BTM site in CAISO/ERCOT pursuing capacity-credit + TOU revenue.
- Provides the round-trip-efficiency and cycle-life numbers the [[bess_4hr_lfp]] entity page synthesizes from.
- Provides the CAPEX range used in early-stage pro-forma — though [[src_legacy_bess_nrel_atb_2024]] is the primary CAPEX source for promotion to reviewed.

## Limitations

- Capacity-credit rules in CAISO and ERCOT are under active discussion (FERC Order 2222 and follow-ons); the "100% at 4 hours" assumption should be re-validated annually.
- Outside CAISO/ERCOT/AZ-style TOU markets, the 4-hour shape may not be the right default. PJM, MISO, NYISO, and ISO-NE all have different capacity-market structures and different on-peak windows.
- The CAPEX range ($230–320/kWh) is from 2024–2025 contracts; the next NREL ATB cycle should refresh this.
- Fire-code reasoning (NFPA 855) is current as of 2024 but actively evolving; jurisdictions like NYC have stricter local rules.
- This note is not a primary source itself — it summarizes CAISO/NREL/Wood Mackenzie. Promotion to reviewed requires re-grounding against those primary sources.

## Related

- [[bess_4hr_lfp]] — entity page that synthesizes this note's rationale into the 4-hour LFP default.
- [[src_legacy_tou_arbitrage|Legacy: TOU arbitrage]] — sibling source explaining the revenue-side reasoning.
- [[src_legacy_bess_nrel_atb_2024]] — sibling source giving the BESS CAPEX trajectory.
- [[bess]] — flowsheet block that consumes this assumption.

## Informs

- BESS sizing default duration in any sizing/dispatch tool downstream.
- Pro-forma CAPEX line for BESS at early stages (pending refresh against NREL ATB).
- Justification for "why 4 hours, not 2 or 6" in any Q&A about BESS choice.

## Source citations the legacy note relied on

- CAISO Resource Adequacy Technical Bulletin 2024-01.
- NREL Annual Technology Baseline 2024, Storage chapter.
- Wood Mackenzie "US Energy Storage Monitor", 2024.
