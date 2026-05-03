---
title: "Legacy note: Cerebras WSE-3"
authority: legacy
status: active
created: 2026-05-02
updated: 2026-05-02
informs: [rack]
scope:
  host_type: [any]
  region: [any]
  equipment: [any]
  voltage_level: [behind_the_meter, distribution]
  applies_when: "AI rack hardware selection when latency-optimized inference at small batch sizes is the dominant workload"
sources:
  - raw/wiki_legacy/hardware/cerebras_wse3.md
related:
  - "[[ai_racks]]"
  - "[[src_legacy_blackwell_gb200_nvl72]]"
approved_by: null
approved_date: null
supersedes: null
---

# Legacy note — Cerebras WSE-3

## Source Summary

Internal hardware brief imported from `raw/wiki_legacy/hardware/cerebras_wse3.md`. Cerebras WSE-3 (Q1 2024 launch) as the wafer-scale alternative for niche latency-optimized inference workloads — specifically time-to-first-token-bound dialogue and agentic pipelines, and memory-bound prefill on very long contexts.

## Key Claims

- Per-wafer compute: ~125 PFLOPS FP16 in a single die — equivalent to ~7 NVIDIA H100s on one wafer, without tensor-parallel interconnect overhead.
- Per-appliance (CS-3): ~23 kW input, 900,000 cores, 44 GB on-wafer SRAM.
- Per-rack density: a full CS-3 is ~43 RU and draws ~23 kW → ~40–50 kW/rack in a typical 48U rack.
- Inference advantage: single-wafer eliminates inter-GPU communication; produces near-best-in-class **time-to-first-token** on large dense models (ms vs tens of ms on GPU clusters).
- When it wins: latency-critical workloads (sub-10ms first-token), memory-bound prefill on >1M-token contexts, transformer-only inference.
- When it loses: throughput-per-dollar bulk inference (GB200 wins), non-transformer workloads (Mamba, diffusion) where porting cost is real.
- Risk: single-vendor architecture; if Cerebras's software stack regresses or roadmap slips, no drop-in replacement exists.

## Engineering Use

- Niche-but-real entry to the platform comparison: justifies why a site committed exclusively to GPU racks may want to reserve floor space for a CS-3 if the workload mix includes latency-bound dialogue or agentic pipelines.
- 40–50 kW/rack density is materially lower than GB200 (~125 kW/rack); same DC budget hosts more rack count but fewer total tokens/s — the platform comparison must specify which throughput metric.
- The vendor-concentration risk is the dominant strategic argument against committing a whole site to CS-3.

## Limitations

- The "20× faster than GPUs on Llama 3.1-70B" figure (Cerebras Inference Service, Aug 2024) is vendor-published and tightly scoped to a specific model + batch size + precision combination.
- The "ms vs tens of ms" first-token claim comes from Cerebras's own marketing; independent third-party verification is limited as of 2024.
- Software ecosystem maturity is the main practical limitation. Tooling is transformer-centric; non-transformer architectures (state-space models, diffusion) require explicit porting work that is not quantified here.
- Single-vendor architecture risk is real: no drop-in replacement, no software-stack alternative, all eggs in one company's roadmap.
- This note is paraphrased; promotion to reviewed requires re-grounding against Cerebras product brief, third-party MLPerf-equivalent benchmarks, and customer case studies.

## Related

- [[ai_racks]] — flowsheet block where this is one of three platform options.
- [[src_legacy_blackwell_gb200_nvl72]] — primary alternative (throughput-bound).
- [[src_legacy_amd_mi300x]] — alternative GPU-level option.

## Informs

- Hardware vendor selection: CS-3 only when latency-bound inference is the dominant workload.
- Rack density assumption for Cerebras-based sites: 40–50 kW/rack.
- Software ecosystem risk assessment when proposing CS-3 in a customer-facing design.

## Source citations the legacy note relied on

- Cerebras CS-3 product brief, cerebras.net/product-system/.
- Cerebras Inference Service launch, Aug 2024 — "20× faster than GPUs on Llama 3.1-70B".
- SemiAnalysis "Cerebras: The Wafer-Scale Bet", 2024-05.
