---
title: "Vault index"
authority: legacy
status: active
created: 2026-05-02
updated: 2026-05-02
---

# Vault index

A catalog of every wiki page. Updated on every ingest, page creation, or
authority change. Pages are listed under the section that matches their
`wiki/` subdirectory. Each entry shows authority level.

**Current state (2026-05-02):**
- Authoritative: 0
- Reviewed: 0
- Candidate: 14
- Legacy: 16
- Total: 30 wiki pages

No pages have been promoted to reviewed or authoritative yet. The vault
is at hardening-pass v0.1: structurally complete, content faithful to
its sources, but the cross-checking work that earns reviewed status has
not yet been done.

---

## Sources

One page summarizing each ingested raw source. Filenames mirror the raw
file slug. All source pages live under `wiki/sources/`. Authority is
`legacy` (imported from earlier work, faithful summary) or `candidate`
(LLM-summarized but not yet cross-checked).

- [[src_legacy_4h_battery_standard]] — 4-hour BESS as industry default. *legacy*
- [[src_legacy_amd_mi300x]] — AMD Instinct MI300X / MI325X. *legacy*
- [[src_legacy_bess_nrel_atb_2024]] — NREL ATB 2024 BESS CAPEX. *legacy*
- [[src_legacy_bifacial_gain]] — bifacial PV yield gain. *legacy*
- [[src_legacy_blackwell_gb200_nvl72]] — NVIDIA GB200 NVL72. *legacy*
- [[src_legacy_cerebras_wse3]] — Cerebras WSE-3 wafer-scale. *legacy*
- [[src_legacy_dc_industry_benchmarks]] — Data center facility CAPEX 2024. *legacy*
- [[src_legacy_dual_axis]] — dual-axis PV tracking. *legacy*
- [[src_legacy_fixed_tilt]] — fixed-tilt PV ground-mount. *legacy*
- [[src_legacy_pv_lazard_lcoe_2024]] — Lazard LCOE+ 2024 PV CAPEX. *legacy*
- [[src_legacy_single_axis_tracker]] — single-axis PV tracker. *legacy*
- [[src_legacy_tou_arbitrage]] — TOU arbitrage as BESS revenue mechanic. *legacy*
- [[src_legacy_tx_ercot_interconnect]] — ERCOT BTM interconnection rules. *legacy*
- [[src_legacy_vera_rubin_nvl144]] — NVIDIA Vera Rubin NVL144 (roadmap). *legacy*
- [[src_legacy_wwtp_buffer_setback]] — WWTP buffer setback rules. *legacy*

## Blocks

Engineering-block role pages — what each flowsheet block represents,
sizing variables, dependencies, source notes. All under `wiki/blocks/`.

- [[ai_racks]] — AI inference rack fleet. *candidate*
- [[bess]] — battery energy storage system. *candidate*
- [[dc_bus]] — DC distribution bus. *candidate*
- [[inverter]] — PV inverter (and BESS PCS). *candidate*
- [[pv_array]] — PV array (default: single-axis bifacial). *candidate*
- [[service_transformer]] — utility service transformer. *candidate*
- [[wwtp_load]] — existing WWTP electrical load profile. *candidate*

## Graphs

Pages about the vault's edge structure: what's candidate vs reviewed,
how promotion works, mapping to the blog series. All under `wiki/graphs/`.

- [[ai_candidate_graph]] — LLM-proposed edges, not yet reviewed. *candidate*
- [[reviewed_engineering_graph]] — human-approved edges, citable as fact. *candidate*

## Concepts

Domain ideas — framings, decisions, or design rules that span multiple
entities. All under `wiki/concepts/`.

- [[behind_the_meter_siting]] — BTM siting thesis. *candidate*
- [[governance_hierarchy]] — Authoritative / Reviewed / Candidate schema. *legacy*

## Entities

Discrete things in the EnergyFlux problem space — specific GPU racks,
BESS configurations, transformer classes, WWTP archetypes. All under
`wiki/entities/`. Entity pages are higher-level syntheses than blocks
and source notes; they may consume multiple sources.

- [[bess_4hr_lfp]] — 4-hour LFP BESS configuration. *candidate*
- [[gb200_nvl72]] — NVIDIA Blackwell GB200 NVL72 platform. *candidate*
- [[wwtp_45mgd_archetype]] — 45 MGD WWTP worked-case archetype. *candidate*

## Synthesis

Cross-cutting analyses, comparisons, decision tables. Often filed back
from query answers. All under `wiki/synthesis/`.

- [[syn_btm_siting_cases]] — comparison of BTM host types. *candidate*

---

**Maintenance note for the LLM maintainer:** Update this index on every
new page creation, rename, or authority-level change. Keep entries
terse — title, one-line summary, current authority. Detailed content
lives on the page itself, not here.
