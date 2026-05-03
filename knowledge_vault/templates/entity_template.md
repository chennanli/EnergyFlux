---
title: "<thing name>"
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

# <thing name>

One-paragraph plain-English description of what this thing is and why it matters in the EnergyFlux problem space.

## Headline numbers

- **<key spec>:** <number with units, with a primary source citation>
- **<key spec>:** <…>
- **<key spec>:** <…>

## Why this is the default / the typical / the right choice (when applicable)

Three to five sentences explaining the structural reasons the thing is what it is, not just what it is.

## When to deviate

- **<edge case 1>:** <when something else is the better choice>
- **<edge case 2>:** <…>

## Open questions for review

- <something the author is not yet sure about and would like reviewer input on>

## Related

- [[<related_page_1>]] — <one-line reason for the link>
- [[<related_page_2>]] — <one-line reason for the link>
