---
title: "Governance hierarchy: Authoritative / Reviewed / Candidate"
authority: legacy
status: active
created: 2026-05-01
updated: 2026-05-02
informs: [none]
scope:
  host_type: [any]
  region: [any]
  equipment: [any]
  voltage_level: [any]
  applies_when: "every wiki page in this vault, every memory artifact in any future LLM-assisted engineering tool"
sources:
  - .auto-memory/governed_engineering_memory.md
related:
  - "[[behind_the_meter_siting]]"
approved_by: null
approved_date: null
supersedes: null
---

# Governance hierarchy: Authoritative / Reviewed / Candidate

The three-level memory governance pattern adopted for this vault, recorded in `.auto-memory/governed_engineering_memory.md` after Codex round-3 discussion on 2026-05-01.

## The levels

- **Authoritative** — external or official source: regulations, vendor official documentation, ISO/IEEE/NERC/NEC standards, peer-reviewed papers, government datasets. The wiki page is a faithful summary; departures from the source are flagged. The LLM may use this auto-citing.
- **Reviewed** — a human-approved synthesis, lesson learned, or design rule. Approved by Chennan or an external engineer he trusts. The wiki page records the approval (`approved_by`, `approved_date`). The LLM may use this auto-citing.
- **Candidate** — a draft or auto-generated synthesis the LLM has produced but Chennan has not yet reviewed. The LLM may surface this in answers but must label it as Candidate; cannot be cited as a primary basis for engineering decisions.
- **Legacy** — content imported from earlier work that has not yet been re-validated under this schema. Treat as Candidate-equivalent until promoted.

The killer rule: **the LLM may auto-use Authoritative and Reviewed; Candidate must be surfaced for human review before influencing decisions.**

## Why this maps to industrial regulatory frameworks

The pattern borrows the governance logic industrial teams already know from PSM, GMP, NERC/CIP, and environmental review — source, scope, approval, effective date, revision history. None of those frameworks accept "an AI agent learned from a session and changed the design rule" as a valid management-of-change. They all require explicit human review and an audit trail. This vault's hierarchy is the AI-tool equivalent.

This page does not claim that the vault is PSM-compliant or GMP-validated; it claims that the *governance logic* is borrowed from those frameworks. Compliance against any specific regulatory framework would require formal validation that has not been done.

## Scope as a first-class field

Authority level is necessary but not sufficient. **Scope** — host type, region, equipment, voltage level, and conditions — is what prevents an Authoritative entry from being mis-applied. An ERCOT BTM interconnection lesson is Authoritative in ERCOT and unsafe to auto-apply in CAISO. An LFP BESS thermal lesson is Authoritative for LFP and unsafe to auto-apply to NMC. Scope mis-application is the most common failure mode in industrial AI tools, more than authority confusion.

## Promotion workflow (planned for Blog 3 demonstration)

The promotion workflow Blog 3 is intended to demonstrate end-to-end:

1. Dispatch session generates a raw event log (Candidate level).
2. Agent summarizes as a Candidate memory entry with auto-extracted scope tags.
3. Engineer reviews; if accepted, the agent rewrites it as a Reviewed entry with full scope metadata, approver, effective date, and source link back to the originating session.
4. On a future similar condition, the copilot surfaces the Reviewed memory and applies it automatically, with citation to the review.

This is structurally different from "AI agent that learns from chat," because every promotion goes through a human gate.

## Open questions

- Whether v2 of this hierarchy needs more granularity (e.g., separating peer-reviewed paper from vendor doc, or separating "approved by Chennan" from "approved by external engineer"). v1 keeps three levels for legibility; v2 expands if real use shows the granularity matters.
- Whether scope fields need additional dimensions (operating regime, climate zone, jurisdiction sub-region). v1 keeps a fixed set.

## Related

- `.auto-memory/governed_engineering_memory.md` — the upstream auto-memory note.
- [[behind_the_meter_siting]] — the substantive thesis where this governance pattern is applied.
