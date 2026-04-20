# NVIDIA Blackwell GB200 NVL72

**Status:** shipping in volume since Q3 2025.
**Role in design:** the default hardware choice when the site needs to be commissioned on known-good numbers.

## Key numbers

* Per-rack facility draw: **125 kW** (72 × B200 GPUs + NVL72 switch + cooling). NVIDIA spec gives 120 kW typical, 132 kW peak; design to 125 kW as the rated facility load.
* Per-rack FP8 compute: **~1.4 EFLOPS** sustained.
* Inference throughput: **~5.8 × 10⁶ tokens/s per MW** on a 70B-parameter dense model at batch 32, FP8.
* Liquid cooling: rear-door heat exchanger or direct-to-chip; facility PUE typically **1.15–1.25**.
* Memory: 192 GB HBM3e per GPU, so 13.8 TB HBM per rack — enough to keep an entire 670B MoE model (DeepSeek V3 class) resident.

## Why it matters for site sizing

Because it's shipping and instrumented, every kW/rack number, thermal curve, and networking constraint is observable from operator data. Design-stage estimates for Blackwell sites carry <5% uncertainty. For Blog 2's 30 MGD headline site (2 MW DC), 2 MW / 125 kW = **16 racks** — the number used throughout the EnergyFlux stage 1.5 simulation.

## When to pick something else

* If the site is budget-constrained and Rubin's advertised 3× token/s-per-kW pans out → reconsider in 2027 after field data exists.
* If the workload is transformer-only inference on a fixed architecture → ASIC alternatives (Cerebras, possibly Etched post-launch) may close the gap on per-query cost.

## Sources

* NVIDIA GB200 NVL72 product brief (nvidia.com/gb200-nvl72), Feb 2024.
* NVIDIA Blackwell architecture white paper, GTC March 2024.
* SemiAnalysis "GB200 Hardware Architecture Deep Dive", 2024-03-19.
