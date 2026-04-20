# Data center CAPEX — industry benchmarks 2024

**Scope:** facility shell + mechanical + electrical + liquid cooling + commissioning for a modern colocated AI inference site. Excludes land acquisition and excludes the GPUs themselves (which are a separate ~$25–35M per MW purchase).

## Key numbers (2024 $, per MW of IT load)

| Component                     | $ / MW IT   | Notes                                |
|-------------------------------|------------|--------------------------------------|
| Building shell + site work    | $1.5 – 2.5 | Steel frame + slab, fence, lighting  |
| Electrical (switchgear+UPS)   | $3.0 – 4.0 | Dual utility feed, redundancy        |
| Mechanical (cooling+CRAH)     | $3.5 – 5.0 | Liquid cooling, rear-door HX, chillers|
| Networking / cabling          | $0.5 – 1.0 | Fiber, structured cabling, racks     |
| Commissioning / EPC margin    | $1.0 – 1.5 | Factory acceptance, QA, contingency  |
| **Total, facility CAPEX**     | **$9.5 – 14.0** | **excludes GPUs**                |

With GPUs (server hardware): add **$25–35M per MW** for Blackwell NVL72-class equipment at retail allocation.

## For the Blog 2 default (2 MW IT colocated site)

* Facility CAPEX midpoint: **$23M** (2 MW × $11.5M/MW).
* GPU CAPEX (Blackwell, 16 racks): **~$60M** (16 × $4M/rack).
* **All-in site CAPEX: ~$83M.**

## Why "cost per MW IT" varies so much

Three drivers:

1. **Cooling modality.** Air-cooled: cheaper build, lower density, higher PUE (~1.35). Liquid: +25% CAPEX, supports Blackwell/Rubin density, PUE ~1.15.
2. **Redundancy tier.** Tier III (concurrently maintainable): baseline number. Tier IV (fault-tolerant): +30–40%.
3. **Regional labor.** CA / NY builds cost ~1.4× TX / NC builds for identical design.

## What's excluded (budget separately)

* **Land acquisition.** At a WWTP buffer, $0 (long-term lease in-kind).
* **Substation upgrade.** $200k–$800k depending on utility capacity.
* **Operations + maintenance.** ~$1.5–2.5M/yr for a 2 MW site, not CAPEX.

## Sources

* JLL Data Center Outlook H2 2024.
* CBRE North America Data Center Trends Report, 2024.
* Uptime Institute Global Data Center Survey, 2024.
* NVIDIA DGX SuperPOD reference architecture guide, 2024.
