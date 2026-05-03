---
title: "<concept name>"
authority: candidate
status: active
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
informs: [<block_id_1>, <block_id_2>]
scope:
  host_type: [<WWTP | chemical | substation | campus | any>]
  region: [<ERCOT | CAISO | MISO | PJM | NYISO | ISO-NE | any>]
  equipment: [<LFP_BESS | NMC_BESS | GB200_NVL72 | any>]
  voltage_level: [<transmission | distribution | behind_the_meter | any>]
  applies_when: "<short condition or 'any'>"
sources:
  - raw/<path/to/source>
related:
  - "[[<related_page_1>]]"
  - "[[<related_page_2>]]"
approved_by: null
approved_date: null
supersedes: null
---

# <concept name>

One-paragraph plain-English description of the concept and why it matters in the EnergyFlux problem space. Concepts are not single things in the world — they are framings, decisions, or design rules that span multiple entities.

## What the concept claims

Three to seven sentences capturing the substantive claim of the concept. State the claim, not just the topic.

## Why this is the substantive choice (when applicable)

Three to five sentences explaining the structural reasons the concept holds, not just the assertion. If the concept is a design rule, this section should make the reader able to recover the rule from first principles.

## Necessary conditions

- **<condition 1>:** <what must be present for the concept to apply>
- **<condition 2>:** <…>
- **<condition 3>:** <…>

## What this concept does *not* claim

- <common over-reading 1>
- <common over-reading 2>

## Open questions for review

- <something the author is not yet sure about and would like reviewer input on>

## Related

- [[<related_page_1>]] — <one-line reason for the link>
- [[<related_page_2>]] — <one-line reason for the link>
