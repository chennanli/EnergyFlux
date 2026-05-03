---
title: "Block: AI racks"
authority: candidate
status: active
created: 2026-05-02
updated: 2026-05-02
informs: [rack]
scope:
  host_type: [WWTP, chemical, substation, campus]
  region: [any]
  equipment: [GB200_NVL72, any]
  voltage_level: [behind_the_meter, distribution]
  applies_when: "AI inference rack platform selection and rack-count sizing"
sources:
  - raw/wiki_legacy/hardware/blackwell_gb200_nvl72.md
  - raw/wiki_legacy/hardware/vera_rubin_nvl144.md
  - raw/wiki_legacy/hardware/amd_mi300x.md
  - raw/wiki_legacy/hardware/cerebras_wse3.md
  - raw/wiki_legacy/capex/dc_industry_benchmarks.md
related:
  - "[[gb200_nvl72]]"
  - "[[src_legacy_blackwell_gb200_nvl72]]"
  - "[[src_legacy_vera_rubin_nvl144]]"
  - "[[src_legacy_amd_mi300x]]"
  - "[[src_legacy_cerebras_wse3]]"
  - "[[src_legacy_dc_industry_benchmarks]]"
  - "[[dc_bus]]"
approved_by: null
approved_date: null
supersedes: null
---

# Block: AI racks

## What this block represents

The fleet of AI inference racks colocated at the BTM site. Blog 2 default is **NVIDIA GB200 NVL72** at 21 racks for the 45 MGD archetype, but the block is platform-agnostic and supports vendor swaps to AMD MI300X, Cerebras WSE-3, or future Vera Rubin NVL144.

This block handles the IT-load side of the site; the cooling, distribution, and grid coupling sit downstream in [[dc_bus]] and [[service_transformer]].

## Key sizing variables

- **Per-rack facility draw (kW)** — vendor-dependent. GB200: 125 kW. Vera Rubin (estimated): 175 kW. AMD MI300X: 60–80 kW. Cerebras: 40–50 kW.
- **Rack count** — `rack_count = total_DC_IT_load / per_rack_facility_kW`.
- **Total DC IT load (MW)** — set by site DC budget after PUE and cooling auxiliaries.
- **Inference throughput (tokens/s/MW)** — model- and batch-dependent; ~5.8 × 10⁶ for Blackwell on 70B-dense FP8 batch 32.
- **Memory per rack** — drives serving-architecture choice (single-rack vs tensor-parallel).
- **Cooling modality** — liquid mandatory for Blackwell+; rack-level rear-door HX or direct-to-chip.

## Upstream dependencies

- **[[dc_bus]]** block: provides DC power. Total DC budget determines rack count.
- **[[service_transformer]]** block: capacity must accommodate AI rack peak + WWTP load + BESS charging.

## Downstream dependencies

- Facility cooling load (CDU pumps, chillers, rear-door HX fans) — sized to total IT load × (PUE − 1).
- Token-revenue side of the pro-forma — driven by tokens/s/MW × utilization × price/token.
- Network and storage infrastructure (out of scope at this block; assumed sufficient).

## Source notes that inform this block

- [[src_legacy_blackwell_gb200_nvl72]] — current default platform.
- [[src_legacy_vera_rubin_nvl144]] — next-gen NVIDIA platform; design-for-future sizing.
- [[src_legacy_amd_mi300x]] — primary GPU-level alternative; capex-per-token argument.
- [[src_legacy_cerebras_wse3]] — wafer-scale niche for latency-bound inference.
- [[src_legacy_dc_industry_benchmarks]] — facility CAPEX context.
- [[gb200_nvl72]] — entity-level synthesis on the default platform.

## Candidate assumptions pending review

- **GB200 at 125 kW/rack** — NVIDIA spec midpoint; real measured field draw at scale is not yet broadly published.
- **Tokens/s/MW = 5.8 × 10⁶** — for one specific model class (70B dense, batch 32, FP8); MoE and longer-context workloads will differ.
- **PUE 1.15–1.25** — liquid cooling, benign ambient; not validated for hot-climate sites.
- **Vera Rubin numbers** — vendor roadmap, ±30% uncertainty bands per [[src_legacy_vera_rubin_nvl144]]; not field-verified.
- **AMD/Cerebras platform comparisons** — tokens/s percentages are MLPerf-derived estimates, not real-workload measurements at the site sizes Blog 2 considers.
- **Rack platform = single-vendor for the whole site** — the block currently models a single platform per site; mixed platforms (some GB200, some MI300X) is plausible but not modeled.

## What would make this block authoritative / reviewed

- **Reviewed**: source notes promoted; senior engineer signs off on the platform-selection decision rule given the project's specific workload, supply situation, and budget. Tokens/s/MW number replaced with a workload-specific number (or banded with explicit uncertainty).
- **Authoritative**: NVIDIA GB200 product brief, AMD MI300X datasheet, Cerebras CS-3 product brief, NVIDIA Vera Rubin roadmap all cited as authoritative source pages directly. The path: promote at least the GB200 source to authoritative; this block then cites it as the default reference and is itself promoted to reviewed.
