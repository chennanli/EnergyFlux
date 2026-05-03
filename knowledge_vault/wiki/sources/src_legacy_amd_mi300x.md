---
title: "Legacy note: AMD Instinct MI300X (and MI325X)"
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
  applies_when: "AI rack hardware selection when NVIDIA supply is constrained or capex-per-token matters more than peak performance"
sources:
  - raw/wiki_legacy/hardware/amd_mi300x.md
related:
  - "[[ai_racks]]"
  - "[[src_legacy_blackwell_gb200_nvl72]]"
  - "[[src_legacy_vera_rubin_nvl144]]"
approved_by: null
approved_date: null
supersedes: null
---

# Legacy note — AMD Instinct MI300X (and MI325X)

## Source Summary

Internal hardware brief imported from `raw/wiki_legacy/hardware/amd_mi300x.md`. AMD Instinct MI300X (Q4 2023 launch) and MI325X (Q4 2024 launch) as the serious GPU-level alternative to NVIDIA when supply allocation is constrained or capex-per-token matters more than peak performance.

## Key Claims

- MI300X per-GPU facility draw: ~750 W. An 8-GPU server chassis (MI300X HGX) lands around 8–10 kW.
- Per-rack density: 60–80 kW/rack in typical 8U chassis configurations — roughly half a GB200 NVL72.
- HBM: **192 GB per GPU** (HBM3), larger than any 2024 NVIDIA SKU. Makes single-GPU inference of 70B–120B models feasible without tensor parallelism.
- Inference throughput: approximately **70–85% of GB200 NVL72** on the same model class, per published MLPerf and independent benchmarks.
- Pricing (2024 secondary market): ~$12–15k per GPU vs NVIDIA B200 ~$30–40k.
- Same 2 MW DC budget hosts proportionally more MI300X servers due to lower per-rack density, but delivers roughly the same tokens/s (lower per-rack power × lower per-rack throughput ≈ cancels out). The win is **CAPEX per tokens/s — often 1.3–1.6× better than NVIDIA at 2025 prices**.

## Engineering Use

- Hardware-side hedge: justifies a budget-sensitive site picking AMD when NVIDIA allocation is uncertain.
- 192 GB HBM enables single-GPU serving of 70B–120B models — relevant for serving architectures that prefer to avoid tensor parallelism.
- Cost-per-token math is the dominant argument — useful when comparing site economics across vendors.

## Limitations

- Per-rack density of 60–80 kW means same DC budget delivers **fewer racks** of MI300X than GB200, which has implications for floor area and cooling distribution that the source does not detail.
- The "70–85% throughput" range is an MLPerf-derived estimate; real workloads with different model sizes, batch sizes, and precisions may deviate substantially.
- Software ecosystem is meaningfully behind NVIDIA's. ROCm has improved through 2024 but a workload that runs cleanly on CUDA may need re-tuning on ROCm. The source does not quantify this engineering cost.
- Pricing is secondary-market 2024 — manufacturer suggested retail and direct allocation to large hyperscalers is different.
- This note is paraphrased; promotion to reviewed requires re-grounding against the AMD MI300X datasheet, MLPerf results, and primary-source vendor RFQs.

## Related

- [[ai_racks]] — flowsheet block where this is the alternative platform.
- [[src_legacy_blackwell_gb200_nvl72]] — primary alternative; the cost-per-token comparison.
- [[src_legacy_vera_rubin_nvl144]] — NVIDIA's next-gen platform; the "wait and see" lever.
- [[src_legacy_cerebras_wse3]] — wafer-scale alternative for latency-bound inference.

## Informs

- Hardware vendor selection decision: AMD on supply hedge or capex-per-token; NVIDIA on density and software ecosystem.
- Rack density assumption for AMD-based sites: 60–80 kW/rack vs ~125 kW/rack for GB200.
- Cost-per-token planning for sites where economics dominate over peak performance.

## Source citations the legacy note relied on

- AMD Instinct MI300X datasheet, 2023.
- AMD MI325X announcement, AMD Advancing AI event, Oct 2024.
- MLPerf Inference v4.1 results (mlcommons.org), 2024.
- TechPowerUp + ServeTheHome reviews, Q1 2024.
