# NVIDIA Vera Rubin NVL144

**Status:** announced GTC 2024; first systems expected **late 2026**.
**Uncertainty:** every quantity here is an estimate. ±30% bands are appropriate until field-commissioned units give ground truth. Do **not** commit site construction schedules to Rubin numbers without a signed NVIDIA delivery contract.

## Key numbers (NVIDIA roadmap, unverified)

* Per-rack facility draw: **~150–250 kW** estimated. Nominal design point ~175 kW. (A figure of "1.4 MW/rack" sometimes cited publicly refers to the *Rubin Ultra NVL576*, a 2028-era SKU with 4× the GPU count — don't confuse the two.)
* Per-rack FP4 compute: **~3.6 × 2024-Blackwell** per NVIDIA's published claim — i.e. order of 5 EFLOPS FP4 per rack.
* Inference throughput: target **~2× tokens/s per kW** vs Blackwell at equivalent workload. Equivalent per-MW target ≈ **1.0–1.2 × 10⁷ tokens/s/MW**.
* Memory: HBM4, claimed ~288 GB per GPU; 288 × 144 ≈ 41 TB HBM per rack.

## Why it matters for site sizing

Same 2 MW DC on Rubin NVL144 = **~11 racks** instead of 16 for Blackwell. Same site can host ~2× the inference throughput. This is the real argument for site owners to plan Rubin-ready power + cooling (150 kW-per-rack-ready busway, liquid-cooled) even if they commission on Blackwell.

## What to tell the user

> "Rubin numbers are NVIDIA's public roadmap, not field-verified. Blog 2 uses them as 'what's possible if claims hold' — the baseline design uses Blackwell."

## Sources

* NVIDIA Rubin roadmap, Jensen Huang keynote, GTC 2024 (March).
* SemiAnalysis "Vera Rubin NVL144: Scaling Blackwell Architecture", 2025-03.
* ExplorTech / SDxCentral coverage of Rubin Ultra power envelope, 2025-05.
