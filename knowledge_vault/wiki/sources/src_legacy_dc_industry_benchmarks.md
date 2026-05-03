---
title: "Legacy note: Data center facility CAPEX benchmarks 2024"
authority: legacy
status: active
created: 2026-05-02
updated: 2026-05-02
informs: [rack, dc_bus]
scope:
  host_type: [WWTP, any]
  region: [any]
  equipment: [GB200_NVL72, any]
  voltage_level: [behind_the_meter, distribution]
  applies_when: "early-stage facility CAPEX modeling for a colocated AI inference site, 2024–2026"
sources:
  - raw/wiki_legacy/capex/dc_industry_benchmarks.md
related:
  - "[[ai_racks]]"
  - "[[dc_bus]]"
  - "[[gb200_nvl72]]"
approved_by: null
approved_date: null
supersedes: null
---

# Legacy note — Data center facility CAPEX benchmarks 2024

## Source Summary

Internal cost brief imported from `raw/wiki_legacy/capex/dc_industry_benchmarks.md`. Summarizes industry benchmarks for facility shell + mechanical + electrical + liquid cooling + commissioning for a modern colocated AI inference site, expressed as $/MW of IT load. Excludes land acquisition and the GPUs themselves (which are a separate ~$25–35M per MW purchase).

## Key Claims

- Total facility CAPEX, 2024 USD per MW IT load: **$9.5–14.0M/MW** (excludes GPUs).
- Component breakdown:
  - Building shell + site work: $1.5–2.5M/MW
  - Electrical (switchgear + UPS): $3.0–4.0M/MW
  - Mechanical (cooling + CRAH): $3.5–5.0M/MW
  - Networking / cabling: $0.5–1.0M/MW
  - Commissioning / EPC margin: $1.0–1.5M/MW
- GPU CAPEX (server hardware): add **$25–35M per MW** for Blackwell NVL72-class equipment at retail allocation.
- Blog 2 default (2 MW IT colocated site): facility ~$23M, GPU ~$60M, all-in ~$83M.
- Three drivers of variability:
  1. Cooling modality — air-cooled is cheaper but caps density at ~40 kW/rack and PUE ~1.35; liquid adds ~25% to CAPEX but enables Blackwell/Rubin density and PUE ~1.15.
  2. Redundancy tier — Tier III is the baseline; Tier IV adds 30–40%.
  3. Regional labor — CA/NY ~1.4× TX/NC for identical design.
- Excluded (separately budgeted): land, substation upgrade ($200k–$800k), O&M (~$1.5–2.5M/yr per 2 MW).

## Engineering Use

- Provides the facility CAPEX line for any pro-forma at design stage.
- Cooling-modality tradeoff is the dominant CAPEX lever — the source justifies why liquid pays for itself at Blackwell density.
- Redundancy and regional labor multipliers are the right knobs for sensitivity analysis.

## Limitations

- 2024 USD; CAPEX is moving rapidly with hyperscaler demand and AI rack density. Promotion to reviewed requires year-current numbers.
- Numbers are for "modern colocated AI inference"; older enterprise data centers, edge sites, and HPC sites all have different cost profiles.
- The $25–35M/MW GPU number is the most volatile — secondary-market Blackwell pricing in 2024 was unusually high; 2026 numbers should be re-checked.
- This note is paraphrased from JLL / CBRE / Uptime Institute reports, which themselves are surveys, not primary-source per-project data. Promotion to reviewed requires either an explicit primary case study or vendor RFQ.

## Related

- [[ai_racks]] — flowsheet block for the AI rack platform.
- [[dc_bus]] — flowsheet block for the DC distribution that this CAPEX includes.
- [[gb200_nvl72]] — entity page for the assumed rack platform.

## Informs

- Facility CAPEX pro-forma line at any sizing stage.
- Cooling-modality decision (always liquid for Blackwell+ density).
- Tier choice trade-off (default to Tier III; flag Tier IV as a 30–40% premium).
- Regional labor adjustment when the WWTP is in CA or NY vs TX or NC.

## Source citations the legacy note relied on

- JLL Data Center Outlook H2 2024.
- CBRE North America Data Center Trends Report, 2024.
- Uptime Institute Global Data Center Survey, 2024.
- NVIDIA DGX SuperPOD reference architecture guide, 2024.
