---
title: "Synthesis: BTM siting host types compared"
authority: candidate
status: active
created: 2026-05-02
updated: 2026-05-02
informs: [grid, wwtp]
scope:
  host_type: [WWTP, chemical, substation, campus]
  region: [any]
  equipment: [any]
  voltage_level: [distribution, behind_the_meter]
  applies_when: "early-stage screening of which industrial host class to pursue for a BTM AI-inference siting strategy"
sources:
  - blog/blog2_v2.html
related:
  - "[[behind_the_meter_siting]]"
  - "[[wwtp_45mgd_archetype]]"
approved_by: null
approved_date: null
supersedes: null
---

# Synthesis — BTM siting host types compared

[[behind_the_meter_siting]] requires three resources: industrially-zoned land, megawatt-class electrical service, and water for cooling. Different industrial host classes satisfy these to different degrees. This page compares the four most plausible classes considered in the EnergyFlux series.

## At-a-glance

| Host class | Industrial land | MW-class service | On-site water | All three reliably? |
|---|---|---|---|---|
| **Mid-size municipal WWTP (25–150 MGD)** | Yes (sized for treatment basins; setbacks have buffer) | Yes (aeration peaks 1–5 MW) | Yes (treated effluent) | **Yes** |
| **Chemical / petrochemical site** | Yes | Often yes | Sometimes (depends on process) | Partial |
| **Distribution substation** | Sometimes (small lots) | Yes by definition | No | Partial |
| **Large institutional campus** (university, hospital, government) | Yes (sometimes) | Sometimes (varies) | Sometimes | Partial |

The diagonal pattern matters: WWTP is the only host class where all three resources are reliably present. The other classes carry one or two of the three. This is the structural reason Blog 2 picks WWTP as the worked case.

## Why each class is partial, not full

**Chemical / petrochemical sites** typically have land and service. Cooling water depends on the specific process: a reformer or cracker has substantial cooling-tower makeup demand, but a finishing or blending facility may not. Selecting "chemical sites" as a host class without specifying the unit operation introduces site-by-site variability that the [[wwtp_45mgd_archetype]] archetype does not have.

**Distribution substations** by definition have megawatt-class service and often have the right industrial zoning. Land area is constrained — substation footprints are typically a few acres at most. Water is essentially never present on-site. A BTM AI factory at a distribution substation is plausible only if cooling water is sourced separately (recycled water from an adjacent municipal source, for instance).

**Large institutional campuses** vary too much to describe as a class. Some research universities have central plants that meet all three criteria; many do not. Government campuses with mature steam plants (military bases, large federal facilities) are interesting but politically harder to negotiate.

## Implication for screening

For an investor or developer doing first-pass screening, the EPA CWNS dataset is uniquely useful: it identifies ~350 mid-size municipal WWTPs in the 25–150 MGD band where the three resources are reliably present. No comparable single-source dataset exists for chemical sites, substations, or campuses. The EnergyFlux Blog 2 thesis leverages this asymmetry.

## What this synthesis does not claim

It does not claim that WWTP is the only viable BTM AI host class — only that WWTP is the host class where the screening data is cleanest. Chemical / substation / campus deployments are plausible site-by-site; they are just not amenable to a single-dataset screening pass at national scale.

## Open questions for review

- Is there an analogous EPA-style dataset for chemical sites that the author has missed? (TRI is close but not directly applicable.)
- Is the "few acres at most" claim about distribution substation footprints accurate at the upper-percentile? Some EHV substations are larger; whether any have the right zoning for BTM compute is an empirical question.

## Related

- [[behind_the_meter_siting]] — the underlying concept.
- [[wwtp_45mgd_archetype]] — the worked example for the WWTP class.
