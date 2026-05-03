---
title: "WWTP 45 MGD archetype (Blog 2 worked case)"
authority: candidate
status: active
created: 2026-05-02
updated: 2026-05-02
informs: [wwtp, grid, pv, bess, rack]
scope:
  host_type: [WWTP]
  region: [ERCOT, CAISO, MISO, PJM, NYISO, ISO-NE]
  equipment: [LFP_BESS, GB200_NVL72]
  voltage_level: [distribution, behind_the_meter]
  applies_when: "first-pass screening of mid-size U.S. municipal WWTPs (25–150 MGD) for BTM AI inference colocation"
sources:
  - raw/wiki_legacy/regulations/wwtp_buffer_setback.md
  - blog/blog2_v2.html
related:
  - "[[behind_the_meter_siting]]"
  - "[[bess_4hr_lfp]]"
  - "[[gb200_nvl72]]"
  - "[[syn_btm_siting_cases]]"
approved_by: null
approved_date: null
supersedes: null
---

# WWTP 45 MGD archetype

The worked-case site profile used as the headline example throughout EnergyFlux Blog 2. Represents a typical U.S. mid-size municipal wastewater treatment plant in the 25–150 MGD flow band that has been screened (per EPA CWNS 2022) as a candidate host for behind-the-meter AI inference colocation.

## Headline parameters

- **Treatment design flow:** 45 MGD (chosen as midpoint of the screened band).
- **Existing peak grid load (WWTP itself):** ~3,750 kW (aeration + pumping + ancillaries, typical for 25–60 MGD).
- **Existing service transformer:** 4 MVA (sized at ~1.07× WWTP peak — the lean end of utility convention).
- **Available buffer-zone land for PV:** ~23 acres post-setback (NFPA / local zoning).

## Worked-case AI factory build (conservative simultaneity, Blog 2 default)

- **PV nameplate:** 7,474 kWp (single-axis bifacial, 580 W TOPCon modules, 11 × 550 kW central inverters at ILR 1.25).
- **BESS:** 10.5 MWh, 4-hour LFP ([[bess_4hr_lfp]]).
- **AI rack count:** 21 racks of [[gb200_nvl72]], 2.62 MW IT load.
- **Peak added grid demand (worst-case simultaneity):** 4,578 kW. Existing 4 MVA transformer cannot serve both WWTP baseline and the new added load simultaneously, so the worked case requires a transformer upgrade.

## Honest scope limits

- **Single-site genericization is fragile.** Real WWTP load varies ±30% with treatment process, climate, and biogas-CHP utilization. The 3,750 kW figure here is a reasonable midpoint, not a guaranteed value.
- **The 23 acres buffer assumption** comes from a typical NFPA-compliant setback geometry. Some sites have less available land (urban WWTPs); some have far more (exurban / regional WWTPs).
- **The 4 MVA transformer assumption** is deliberately tight (1.07× peak). Many real-world WWTPs are sized at 1.4× WWTP peak (5–6 MVA) — see [[syn_btm_siting_cases]] for the typical-vs-lean comparison.

## Open questions for review

- The "23 acres available after setback" assumption needs validation against a few real plants (DC Water, Oakland EBMUD, Austin Walnut Creek would be diagnostic).
- The 3,750 kW WWTP load is an assumption on Aspen-style heuristics; a survey of EPA EnergyStar Portfolio Manager data could pin the median for 25–60 MGD plants.

## Related

- [[behind_the_meter_siting]] — concept this archetype is an instance of.
- [[bess_4hr_lfp]] — the storage configuration.
- [[gb200_nvl72]] — the rack platform.
- [[syn_btm_siting_cases]] — comparison across host types and sizing assumptions.
