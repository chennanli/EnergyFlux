---
title: "4-hour LFP BESS (industry default)"
authority: candidate
status: active
created: 2026-05-02
updated: 2026-05-02
informs: [bess]
scope:
  host_type: [WWTP, any]
  region: [CAISO, ERCOT, any]
  equipment: [LFP_BESS]
  voltage_level: [distribution, behind_the_meter]
  applies_when: "BESS sized for energy arbitrage / TOU shaving / capacity contribution; not for sub-second grid services"
sources:
  - raw/wiki_legacy/bess/4h_battery_standard.md
  - raw/wiki_legacy/bess/tou_arbitrage.md
related:
  - "[[src_legacy_4h_battery_standard]]"
  - "[[behind_the_meter_siting]]"
  - "[[wwtp_45mgd_archetype]]"
  - "[[governance_hierarchy]]"
approved_by: null
approved_date: null
supersedes: null
---

# 4-hour LFP BESS (industry default)

The default BESS configuration for utility-scale and behind-the-meter installations in the U.S. as of 2024–2026: lithium iron phosphate (LFP) chemistry, sized so that nameplate energy capacity equals four hours of nameplate discharge power.

## Why "4 hours"

Three forces converge on this duration ([[src_legacy_4h_battery_standard]]):

1. **Capacity-credit accreditation.** CAISO and ERCOT both grant ~100% capacity credit to 4-hour batteries; 2-hour gets ~60%. Resource-adequacy revenue is a meaningful fraction of project NPV in those markets, so going below 4h is hard to justify economically.
2. **TOU evening-peak coverage.** Most CA / TX / AZ TOU tariffs define the on-peak window as 4 PM – 9 PM (5 hours). A 4-hour battery charged to 85% SOC by 4 PM can carry most of that window.
3. **Fire-code / energy-density envelope.** A 4-hour Li-ion BESS at ~2 MWh fits a standard 20-ft container with NFPA 855-compliant separation. Longer durations either need more footprint or different chemistry.

## Headline numbers

- Round-trip efficiency: **~92%** for modern LFP at moderate C-rate.
- Cycle life: **~6,000 cycles** at 80% depth of discharge.
- Installed CAPEX, 2024–2025 utility scale: **$230–320 / kWh** of usable capacity.
- Capacity fade: **~2.5%/yr**; typical augmentation plan refreshes ~20% of cells at year 10 to maintain rated capacity through year 20.

## When to deviate from the default

- **Fast-cycling grid services** (frequency regulation, voltage support) → 1–2 hour duration is common, because cycle count per day is high and longer duration costs do not pay back.
- **Seasonal time-shift** (storing summer for winter or vice versa) → Li-ion is a bad fit; flow batteries (vanadium, iron-air) at 8–12+ hour duration win on $/kWh-throughput at very long cycles.
- **Behind-the-meter colocated with constant load** (e.g., a co-located AI factory) → 4 hours remains the right default unless the use case is dispatch-heavy enough to justify a separate optimization.

## Open questions for review

- The CAPEX range ($230–320/kWh) is from 2024–2025 contracts; the next NREL ATB update should refresh this.
- Capacity-credit rules in CAISO and ERCOT are under active discussion (FERC Order 2222 and follow-ons); the "100% at 4 hours" assumption should be re-validated annually.

## Related

- [[src_legacy_4h_battery_standard]] — the legacy note this page synthesizes.
- [[behind_the_meter_siting]] — where this BESS configuration is the storage default.
- [[wwtp_45mgd_archetype]] — the worked Blog 2 case using a 4-hour LFP BESS.
- [[governance_hierarchy]] — promote this page to `reviewed` after a citation pass.
