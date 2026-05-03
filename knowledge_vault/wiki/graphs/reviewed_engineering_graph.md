---
title: "Reviewed engineering graph"
authority: candidate
status: active
created: 2026-05-02
updated: 2026-05-02
informs: [governance, none]
scope:
  host_type: [any]
  region: [any]
  equipment: [any]
  voltage_level: [any]
  applies_when: "any engineering decision drawn from the vault that requires citable cross-page support"
sources:
  - scripts/wiki_graph_manifest.py
related:
  - "[[ai_candidate_graph]]"
  - "[[governance_hierarchy]]"
  - "[[behind_the_meter_siting]]"
approved_by: null
approved_date: null
supersedes: null
---

# Reviewed engineering graph

## What this is

The **reviewed engineering graph** is the subset of vault edges that a human reviewer has read, evaluated, and explicitly approved. Each reviewed edge has the property that the relationship between the two pages is **correct, scope-appropriate, and free of known contradictions** as of the approval date. Reviewed edges are the only edges the AI assistant may use as a primary basis for engineering recommendations.

## Reviewed edges *can* drive engineering conclusions

The killer rule: **only reviewed edges can be cited as fact in engineering decisions.** When the AI assistant traces a chain of reasoning that crosses an edge, the chain is only as strong as the weakest edge in it. An answer that depends entirely on reviewed edges can be cited; an answer that crosses any candidate edge must be tagged "pending review."

## How edges become reviewed

An edge is promoted from [[ai_candidate_graph]] to this graph through one of two mechanisms:

1. **Page-level review.** When a vault page is promoted from `authority: candidate` to `authority: reviewed`, the human reviewer is responsible for explicitly endorsing the inbound and outbound edges of that page. The reviewed page's frontmatter records the approver and date; the edges are inherited from the page's review.
2. **Edge-level review.** A reviewer opens a PR that promotes a specific edge between two pages, even when neither page is yet promoted. This is the path for edges that span pages at different authority levels (e.g., an authoritative source-note page connecting to a candidate block page — the connection itself can be reviewed even if the block isn't fully ready).

In both cases, the review must include:

- **Reviewer identity** (name + role).
- **Date of review** (absolute date, not relative).
- **Reasoning** (why the edge is correct, what scope it applies to, what evidence supports it).
- **Effective date** (some reviewed edges are time-bound; e.g., a 2024 NREL ATB number is reviewed-as-of-2024 and may need re-review when 2026 ATB ships).

## What's reviewed today

As of 2026-05-02, **zero edges have been promoted to reviewed.** Every edge in the vault is candidate or legacy. The current state is honest: the vault is in early build-out.

The first batch of likely candidates for promotion (when this work is done):

- `[[gb200_nvl72]]` ↔ `[[src_legacy_blackwell_gb200_nvl72]]` — the entity page faithfully synthesizes the legacy source.
- `[[bess_4hr_lfp]]` ↔ `[[src_legacy_4h_battery_standard]]` ↔ `[[src_legacy_bess_nrel_atb_2024]]` — the duration argument, cross-checked against the CAPEX argument.
- `[[wwtp_45mgd_archetype]]` ↔ `[[src_legacy_wwtp_buffer_setback]]` — the 0.90 land-fraction assumption, when cross-checked against a real plant survey.

None of these is in the reviewed graph yet because the cross-checking work has not been done.

## Promotion workflow (operational steps)

The intended workflow, when v1 of the vault is ready to support reviews:

1. Reviewer reads the candidate page and its inbound/outbound edges via the rendered wiki (`wiki/`).
2. Reviewer fills in the page's `approved_by` and `approved_date` frontmatter fields.
3. Reviewer opens a PR with the change.
4. Branch protection on `main` requires the reviewer to be in the maintainers list (configured in the GitHub repo settings, not in the vault itself).
5. On merge, the page is reviewed; downstream tooling (RAG, wiki publisher) treats the page as primary.
6. A `log.md` entry records the promotion with reviewer, date, and the list of edges promoted.

In v0 (today), branch protection is not configured and no reviewers are designated. Setting these up is part of the Blog 3 governance demo.

## Mapping to Blog 3 / 5 / 6

This graph is the **payload** of the governed-memory theme that runs through Blog 3–6:

- **Blog 3** demonstrates the candidate→reviewed promotion via a worked dispatch session: real events generate candidate edges; a senior engineer reviews; the reviewed graph grows by a documented amount.
- **Blog 5 / 5.5** ground specific entity pages by re-checking against primary sources (NREL ATB, IEEE C57.91, FERC Order 2222), promoting them and their inbound edges.
- **Blog 6** demonstrates surrogate-model results (the engineering surrogate plus uncertainty quantification flagship) — those results, when validated, become reviewed-edge contributions to the graph.

Each post should target a specific number of edge promotions. The visible measure of "the project is real" is the growth of the reviewed graph relative to the candidate graph.

## Relationship to `scripts/wiki_graph_manifest.py`

`wiki_graph_manifest.py` is a hand-curated knowledge graph figure used in Blog 2 to show how source notes attach to engineering blocks. The figure does not distinguish candidate from reviewed edges. A future revision should:

- Render reviewed edges in solid bold.
- Render candidate edges in light dashed.
- Auto-export from frontmatter rather than a hand-curated manifest.

## Open questions for review

- Granularity of "reviewed": should the unit of review be the edge, the page, or a coherent cluster? v0 reviews the page (and inherits its edges); v1 may add edge-level review for cross-authority cases.
- Time-bounded reviews: should a reviewed edge automatically downgrade to candidate after some period (e.g., 2 years)? v0 doesn't enforce this; v1 may.
- Multi-reviewer requirement: should some edges require ≥2 approvals (especially around safety-critical decisions like fire-code or interconnection)? v0 single-reviewer; v1 may extend.

## Related

- [[ai_candidate_graph]] — the upstream pool from which reviewed edges are promoted.
- [[governance_hierarchy]] — the authority schema this graph operationalizes.
- [[behind_the_meter_siting]] — the central concept whose reasoning chain this graph eventually supports.
