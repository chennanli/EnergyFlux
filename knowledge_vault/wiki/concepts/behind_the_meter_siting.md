---
title: "Behind-the-meter (BTM) siting for AI inference"
authority: candidate
status: active
created: 2026-05-02
updated: 2026-05-02
informs: [grid, wwtp, rack, bess, pv]
scope:
  host_type: [WWTP, chemical, substation, campus]
  region: [any]
  equipment: [any]
  voltage_level: [distribution, behind_the_meter]
  applies_when: "siting decisions for new AI inference loads colocated with an existing industrial facility"
sources:
  - blog/blog1_v22.html
  - blog/blog2_v2.html
related:
  - "[[wwtp_45mgd_archetype]]"
  - "[[bess_4hr_lfp]]"
  - "[[gb200_nvl72]]"
  - "[[syn_btm_siting_cases]]"
approved_by: null
approved_date: null
supersedes: null
---

# Behind-the-meter (BTM) siting for AI inference

The thesis underlying the EnergyFlux blog series: some existing industrial facilities in the U.S. already have on-site combinations of permitted industrial land, megawatt-class electrical service, and process water — and could host new behind-the-meter AI inference compute on a distribution-level service-upgrade timeline rather than the multi-year transmission-interconnection-queue timeline a greenfield AI factory would face.

## Why "behind the meter" is the substantive choice

A new AI factory built greenfield typically needs a high-voltage (transmission-class) interconnection. The interconnection queue in most U.S. regions currently runs 3 to 7 years (the figure varies by region and is widely cited but rarely precise). Behind-the-meter colocation puts the new load on the existing site's distribution-level service. The work shifts from "transmission queue" to "service-transformer upgrade," which is a months-scale, distribution-level engineering process — not zero work, but a different category of timeline.

## Necessary conditions for a BTM-viable site

Three resources must already be present on-site:

1. **Industrially-zoned land** with permitting precedent for high-density compute (or buffer/setback land that can accommodate it).
2. **A megawatt-class electrical service** with enough headroom — or a service that can be upgraded distribution-side without requiring a new transmission-level interconnection.
3. **Water for cooling**, ideally process water (treated effluent, cooling-tower blowdown, or similar) to reduce competition with potable supply.

Different industrial host types satisfy these to different degrees. See [[syn_btm_siting_cases]] for a per-host-type breakdown.

## Why WWTPs are the worked case in Blog 2

Mid-size municipal WWTPs (25–150 MGD) reliably combine all three resources: industrially-zoned site land at scale, a megawatt-class service designed for aeration peaks, and treated effluent that is suitable (often after light polishing) for cooling-tower makeup. Roughly 350 such plants exist in the United States (EPA CWNS 2022). The [[wwtp_45mgd_archetype]] page captures the worked example.

## What BTM siting does *not* claim

- It does not eliminate utility coordination. A distribution-level service upgrade still needs the utility's blessing and typically a service study.
- It does not eliminate permitting. Local zoning, NFPA fire codes, and possibly NPDES discharge modifications still apply.
- It does not by itself change the project's engineering risk profile to "trivial." It changes a multi-year interconnection bottleneck to a months-scale distribution bottleneck — a meaningful improvement, not a free pass.

## Open questions

- For host types other than WWTP (chemical, substation, campus), the pieces of the siting stack present vary; [[syn_btm_siting_cases]] compares them.
- The "3 to 7 years" greenfield timeline range is widely cited but not pinned to a single canonical source. A future ingest of the FERC interconnection queue annual report would let this page move from `candidate` to `reviewed`.

## Related

- [[wwtp_45mgd_archetype]] — concrete worked-case archetype.
- [[bess_4hr_lfp]] — the default storage configuration in BTM.
- [[gb200_nvl72]] — the default AI rack platform in BTM.
- [[syn_btm_siting_cases]] — comparison across BTM host types.
