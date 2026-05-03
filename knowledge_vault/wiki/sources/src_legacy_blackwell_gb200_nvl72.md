---
title: "Legacy note: NVIDIA Blackwell GB200 NVL72"
authority: legacy
status: active
created: 2026-05-02
updated: 2026-05-02
informs: [rack]
scope:
  host_type: [WWTP, any]
  region: [any]
  equipment: [GB200_NVL72]
  voltage_level: [behind_the_meter, distribution]
  applies_when: "AI rack hardware selection at the design or sizing stage, 2024–2027 timeframe"
sources:
  - raw/wiki_legacy/hardware/blackwell_gb200_nvl72.md
related:
  - "[[gb200_nvl72]]"
  - "[[ai_racks]]"
approved_by: null
approved_date: null
supersedes: null
---

# Legacy note — NVIDIA Blackwell GB200 NVL72

## Source Summary

Internal hardware brief imported from `raw/wiki_legacy/hardware/blackwell_gb200_nvl72.md`. Single-page summary of the NVIDIA Blackwell GB200 NVL72 rack platform: per-rack power, per-rack compute, inference throughput, memory, cooling. Used as the default AI rack platform for EnergyFlux Blog 2 worked-case sizing.

## Key Claims

- Per-rack facility draw: ~125 kW (NVIDIA spec: 120 kW typical, 132 kW peak).
- Per-rack FP8 compute: ~1.4 EFLOPS sustained.
- Inference throughput: ~5.8 × 10⁶ tokens/s per MW for 70B-dense models at batch 32 FP8.
- Cooling: liquid (rear-door HX or direct-to-chip); facility PUE 1.15–1.25.
- Memory: 192 GB HBM3e per GPU → 13.8 TB HBM per rack — sufficient to keep a 670B-class MoE model resident.
- Worked sizing example: 2 MW DC ÷ 125 kW/rack ≈ 16 racks (the original stage-1.5 30 MGD case). The Blog 2 45 MGD archetype scales this to 2.62 MW DC ÷ 125 kW ≈ 21 racks.

## Engineering Use

- Provides the per-rack power and inference numbers used to size AI rack count for any DC budget at design stage.
- Anchors the [[gb200_nvl72]] entity page and the [[ai_racks]] block.
- Sets the platform comparison baseline for Vera Rubin, AMD MI300X, and Cerebras alternatives — see those source notes for relative throughput.

## Limitations

- The 5.8 × 10⁶ tokens/s/MW figure is for a specific model class (70B dense, batch 32, FP8). MoE models, longer-context workloads, or different precisions will produce different numbers.
- Facility PUE 1.15–1.25 assumes liquid cooling and a benign ambient regime. Hot-climate WWTP sites in TX / AZ may push PUE higher.
- Per-rack draw of 125 kW is the design-point. Real operator data shows 120 kW typical; 132 kW peak is achievable but not sustained.
- Blackwell shipping data is from public NVIDIA materials; field-commissioned numbers from large hyperscaler deployments are not yet broadly published.
- This note is a summary of NVIDIA primary sources; promotion to reviewed requires re-grounding against the GB200 NVL72 product brief and Blackwell architecture white paper directly.

## Related

- [[gb200_nvl72]] — entity page synthesizing rack-platform decisions for design.
- [[src_legacy_vera_rubin_nvl144]] — successor platform; relevant for "design now, deploy later" decisions.
- [[src_legacy_amd_mi300x]] — primary GPU-level alternative.
- [[src_legacy_cerebras_wse3]] — wafer-scale alternative for latency-bound inference.
- [[ai_racks]] — flowsheet block that consumes this hardware selection.

## Informs

- Rack count math: rack_count = facility_DC_load_kW / 125 kW.
- Cooling specification: liquid is mandatory for this platform; design must include rear-door HX or direct-to-chip plumbing.
- HBM headroom: any model up to ~670B parameters fits in a single rack's HBM, which simplifies serving architecture.
- Inference cost-per-token planning baseline against which to compare AMD/Cerebras alternatives.

## Source citations the legacy note relied on

- NVIDIA GB200 NVL72 product brief, Feb 2024.
- NVIDIA Blackwell architecture white paper, GTC March 2024.
- SemiAnalysis "GB200 Hardware Architecture Deep Dive", 2024-03-19.
