---
title: "Legacy note: NVIDIA Vera Rubin NVL144"
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
  applies_when: "AI rack hardware selection for sites being designed for late-2026 / 2027 commissioning"
sources:
  - raw/wiki_legacy/hardware/vera_rubin_nvl144.md
related:
  - "[[ai_racks]]"
  - "[[src_legacy_blackwell_gb200_nvl72]]"
approved_by: null
approved_date: null
supersedes: null
---

# Legacy note — NVIDIA Vera Rubin NVL144

## Source Summary

Internal hardware brief imported from `raw/wiki_legacy/hardware/vera_rubin_nvl144.md`. NVIDIA's Vera Rubin NVL144 platform (announced GTC 2024, first systems expected late 2026) as the next-generation NVIDIA platform after Blackwell. The note explicitly flags that all numbers are vendor roadmap estimates with ±30% uncertainty bands and warns against committing site construction to Rubin numbers without a signed delivery contract.

## Key Claims

- Per-rack facility draw: **~150–250 kW** estimated; nominal design point ~175 kW. (The "1.4 MW/rack" figure sometimes cited refers to a different, 2028-era SKU — Rubin Ultra NVL576 — and should not be confused with NVL144.)
- Per-rack FP4 compute: ~3.6× Blackwell per NVIDIA's published claim, on the order of 5 EFLOPS FP4 per rack.
- Inference throughput target: ~2× tokens/s per kW vs Blackwell at equivalent workload, equivalent per-MW target ~1.0–1.2 × 10⁷ tokens/s/MW.
- Memory: HBM4, ~288 GB per GPU; 288 × 144 ≈ 41 TB HBM per rack.
- Sizing implication: same 2 MW DC on Rubin NVL144 ≈ 11 racks instead of 16 for Blackwell. Same site can host ~2× the inference throughput.
- The argument for "Rubin-ready" power + cooling design (150 kW/rack busway, liquid-cooled) on sites being commissioned on Blackwell today.

## Engineering Use

- Justifies designing service-transformer + busway + cooling capacity for Rubin (175 kW/rack design point) even when commissioning on Blackwell — avoids a forklift upgrade in 2028.
- Provides the "design-for-future" rack count target when the project pencils on Rubin's 2× throughput-per-kW.
- Anchors the conversation about "what's possible if NVIDIA delivery hits roadmap" vs "what's deliverable today."

## Limitations

- **Every quantity here is a roadmap estimate, not a measured outcome.** ±30% bands are appropriate. Field-commissioned units do not yet exist.
- "Late 2026" first-systems date is NVIDIA's announced target; large-program commits should not assume this date.
- The "2× tokens/s per kW vs Blackwell" claim is workload-specific; real workloads may show smaller or larger gains depending on model class, batch size, precision.
- Memory + interconnect numbers are roadmap; HBM4 supply chain is constrained.
- Confusion risk with Rubin Ultra NVL576 (different SKU, 2028-era, different power envelope) is acknowledged but easy to repeat.
- This note is paraphrased; promotion to reviewed requires either NVIDIA primary briefing under NDA, or first field-commissioning data once it exists.

## Related

- [[ai_racks]] — flowsheet block where this is the "design for the future" lever.
- [[src_legacy_blackwell_gb200_nvl72]] — current-generation platform; the baseline for any "deploy today" site.

## Informs

- Service-transformer and busway sizing: design to Rubin-ready (175 kW/rack) rather than Blackwell-only (125 kW/rack), to avoid a forklift upgrade.
- Cooling design: liquid only, capable of 175 kW/rack heat rejection.
- Pro-forma sensitivity: "what if Rubin delivers on time" is a key sensitivity in any 2027-commissioning-onwards site model.

## Source citations the legacy note relied on

- NVIDIA Rubin roadmap, Jensen Huang keynote, GTC 2024 (March).
- SemiAnalysis "Vera Rubin NVL144: Scaling Blackwell Architecture", 2025-03.
- ExplorTech / SDxCentral coverage of Rubin Ultra power envelope, 2025-05.
