# Cerebras WSE-3

**Status:** shipping since Q1 2024 in CS-3 appliances.
**Role in design:** the "niche but real" entry — a wafer-scale alternative when the workload is specifically latency-optimized inference at small batch sizes.

## Key numbers

* Per-wafer compute: **~125 PFLOPS FP16** in a single die — equivalent to ~7 NVIDIA H100s on one wafer, without tensor-parallel interconnect overhead.
* Per-appliance (CS-3): ~23 kW input, 900,000 cores, 44 GB on-wafer SRAM.
* Per-rack density: a full CS-3 is ~43 RU and draws ~23 kW, so roughly **40–50 kW/rack** in a typical 48U rack.
* Inference advantage: single-wafer eliminates inter-GPU communication; produces near-best-in-class **time-to-first-token** on large dense models (measured in ms vs. tens of ms on GPU clusters).

## When it wins

* Latency-critical workloads where the user will pay for sub-10ms first-token — dialogue, agentic pipelines with many serial steps.
* Memory-bound prefill on very large contexts (>1M tokens) where on-wafer SRAM bandwidth vs HBM DDR becomes the bottleneck.

## When it loses

* Throughput-per-dollar workloads (batch 32+ inference at bulk pricing) where GB200 beats CS-3 on $/Mtoken.
* Any workload that isn't a transformer. Cerebras's tooling is transformer-centric; porting a non-transformer (Mamba, diffusion) costs real engineering time.

## Risks for site planning

Single-vendor architecture. If Cerebras's software stack regresses or the company's roadmap slips, a site committed to CS-3 has no drop-in replacement. GB200 and MI300X are both full GPU ecosystems that degrade gracefully.

## Sources

* Cerebras CS-3 product brief, cerebras.net/product-system/.
* Cerebras Inference Service launch, Aug 2024 — "20× faster than GPUs on Llama 3.1-70B".
* SemiAnalysis "Cerebras: The Wafer-Scale Bet", 2024-05.
