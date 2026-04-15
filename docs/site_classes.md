# Industrial Site Classes — Screening Matrix

This document compares industrial site classes as potential hosts for
behind-the-meter AI infrastructure. It is a screening tool, not a ranking.
Each site class has different strengths and constraints; the right choice
depends on the specific site, owner, regulatory environment, and AI workload.

---

## Screening Matrix

| Site class | Electrical headroom | Land availability | Cooling / water | Zoning / permitting advantage | 24/7 ops | Internal AI demand | Likely scale range | Key risks |
|---|---|---|---|---|---|---|---|---|
| **Municipal WWTP** | Medium (existing 4–5 MVA) | Medium–high (mandatory buffer) | High (treated effluent) | Strong — industrial utility parcel, BTM classification clean | High | Medium | MW-scale to low tens-of-MW | Public-sector procurement, H₂S corrosion, municipal budget cycles |
| **Specialty chemical plant** | Medium–high | Medium (EPA RMP setback) | Medium–high | Strong industrial zoning, site-specific complexity | High | High | MW-scale to tens-of-MW | Safety review, process integration, proprietary data constraints |
| **Refinery / large industrial campus** | High | High (large PSM setback) | High | Strong industrial footprint, heavier regulatory overlay | High | High | Tens-of-MW and above | Regulatory burden, brownfield complexity, high capex |
| **Food / beverage processing plant** | Medium | Medium | Medium–high | Often workable, less universally advantaged | Medium–high | Medium | MW-scale to tens-of-MW | Seasonal loads, less obvious AI density |
| **Landfill / brownfield industrial land** | Low–medium | High | Low | Land available, utility side varies widely | Low | Low | Site-dependent | Weak power/water stack, remediation constraints |
| **Rail yard / logistics hub** | Medium | Medium | Low | Industrial zoning helps | High | Medium | MW-scale | Weak cooling stack, fragmented site control |
| **Airport support / industrial park** | Medium–high | Medium | Low–medium | Site-specific, often constrained by aviation/security | High | Medium | MW-scale to tens-of-MW | Permitting complexity, security, non-uniform utilities |

---

## Why WWTP Is the First Case Study

WWTP is not "the winner" in every scenario. It is one unusually complete package
for an initial municipal / utility-adjacent case study.

The combination that makes WWTP compelling as a starting point:
- mandatory buffer land (legally required to stay empty, generates zero revenue)
- existing industrial-grade electrical connection (no new interconnection needed)
- continuous treated water supply (liquid cooling without new water permits)
- 24/7 operations staff and physical security already in place
- heavy industrial zoning (data center permitted as equipment installation)

Among common industrial site classes, municipal WWTPs are unusual in combining all five in a single parcel. Other classes typically have some of these but not all — which is why WWTP is a useful starting case, not because it's universally optimal.

Chemical plants and larger industrial campuses may be better for:
- higher-value private industrial AI
- larger scale deployments
- sites where the operator already has strong internal AI demand

---

## Scale Notes

- **MW-scale to tens-of-MW** is the initial practical wedge for distributed municipal and smaller industrial sites
- This is not a hard ceiling — some industrial campuses can support larger deployments
- The design logic (BTM permitting, transformer headroom, BESS asymmetry) changes at larger scale
- The WWTP case study focuses on the MW-scale case as the most accessible entry point

---

## What Changes at Larger Scale

Once site power demand exceeds the existing substation capacity significantly,
the BTM permitting advantage may reduce:
- larger interconnection upgrades may trigger utility review similar to new connections
- cooling water volumes may require new permits
- the "equipment installation" permitting classification may not hold

The right framing is: **BTM advantage is strongest in the MW-scale to low tens-of-MW range
for existing industrial parcels**. Above that, site-specific engineering analysis is required.

---

*Last updated: April 2026*
*This is a working document. Expand as more case studies are implemented.*
