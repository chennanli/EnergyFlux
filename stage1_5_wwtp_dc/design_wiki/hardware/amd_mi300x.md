# AMD Instinct MI300X (and MI325X)

**Status:** MI300X shipping since Q4 2023; MI325X launched Q4 2024.
**Role in design:** the serious alternative to NVIDIA when either (a) supply allocation from NVIDIA is constrained, or (b) price-per-token matters more than peak performance.

## Key numbers

* MI300X per-GPU facility draw: ~750 W. An 8-GPU server chassis (MI300X HGX) lands around 8–10 kW.
* Per-rack density: roughly 60–80 kW/rack in typical 8U chassis configurations — ~half the density of a GB200 NVL72.
* HBM: **192 GB per GPU** (HBM3), larger than any 2024 NVIDIA SKU. Makes single-GPU inference of 70B–120B models feasible without tensor parallelism.
* Inference throughput: approximately **70–85% of GB200 NVL72** on same model, per published MLPerf and independent benchmarks.
* Price: public list around $12–15k per GPU vs NVIDIA B200 ~$30–40k (secondary market).

## Why it matters for site sizing

Same 2 MW DC budget hosts proportionally more MI300X servers due to lower per-rack density, but **delivers roughly the same tokens/s** (lower per-rack power × lower per-rack throughput ≈ cancels out). The real win is CAPEX per tokens/s — often 1.3–1.6× better than NVIDIA at 2025 prices.

## When to pick it

* Budget-sensitive sites where capex per token matters more than raw peak.
* Workloads that fit in single-GPU memory (inference of 70B–120B models) — MI300X's 192 GB is a genuine product-level advantage.
* Supply hedge: if NVIDIA allocation to your customer tier is uncertain.

## Sources

* AMD Instinct MI300X datasheet, 2023.
* AMD MI325X announcement, AMD Advancing AI event, Oct 2024.
* MLPerf Inference v4.1 results (mlcommons.org), 2024.
* TechPowerUp + ServeTheHome reviews, Q1 2024.
