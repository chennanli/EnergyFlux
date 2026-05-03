---
title: "AI candidate graph"
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
  applies_when: "any LLM-assisted ingest pass that proposes new edges between vault pages"
sources:
  - scripts/wiki_graph_manifest.py
related:
  - "[[reviewed_engineering_graph]]"
  - "[[governance_hierarchy]]"
  - "[[behind_the_meter_siting]]"
approved_by: null
approved_date: null
supersedes: null
---

# AI candidate graph

## What this is

The **AI candidate graph** is the set of edges between vault pages that the LLM (Claude, Codex, future agents) has *suggested* during ingest, query, or synthesis passes — but that **no human has reviewed or approved**. Examples of candidate edges:

- "[[bess_4hr_lfp]] cites [[src_legacy_4h_battery_standard]]" — proposed by the LLM that wrote the entity page from the source note.
- "[[wwtp_45mgd_archetype]] depends on [[src_legacy_wwtp_buffer_setback]]" — proposed by the LLM extracting the 0.90 land-fraction assumption.
- "[[pv_array]] uses default [[src_legacy_single_axis_tracker]] with [[src_legacy_bifacial_gain]]" — proposed by the LLM building the block page.

These edges may be correct. They may also be subtly wrong: an LLM can propose an edge that looks structurally right but cites the wrong source, applies a number outside its scope, or introduces a contradiction with a different page.

## Candidate edges are not facts

The killer rule: **candidate edges in this graph cannot be cited as fact.** They are proposals waiting for review.

When the AI assistant retrieves over the vault, candidate edges may inform the answer (the assistant may follow a candidate edge to surface a related page), but every chain that depends on a candidate edge must be tagged "pending review" in the answer.

## How candidate edges enter the graph

1. **Wikilink resolution at ingest.** When the LLM writes a new vault page, every `[[target]]` it includes becomes a candidate edge. The wiki publisher (`scripts/build_wiki.py`) resolves the link if the target exists, but does not validate that the relationship is correct.
2. **Frontmatter `related:` field.** Every page declares related pages in its frontmatter. These are candidate edges by default.
3. **Synthesis passes.** When the LLM runs a synthesis (e.g., "compare BESS chemistries"), it may propose new edges between previously-unconnected pages. These remain candidate.

## Promotion workflow (Candidate → Reviewed)

A candidate edge is promoted to a [[reviewed_engineering_graph]] edge through one of two paths:

1. **Page-level review.** A human reviewer reads both ends of the edge, confirms the relationship is correct, and updates the page frontmatter to `authority: reviewed` with `approved_by` and `approved_date`. All edges *into* and *out of* the reviewed page that the reviewer explicitly endorsed in the review are promoted.
2. **Edge-level review.** The reviewer opens a PR that adds an edge to a curated list of reviewed edges (proposed: `wiki/graphs/reviewed_edges.yaml`, currently not yet implemented), with an explicit "approved by / date / reasoning" record.

In v0 of the vault (today, 2026-05-02), no edges have been promoted. Every edge in the vault is candidate.

## Mapping to Blog 3 / 5 / 6

The AI candidate graph maps directly onto the **Blog 3–6 cross-cutting governed-memory theme**:

- **Blog 3** is intended to demonstrate the promotion workflow end-to-end: a dispatch session generates raw events; the LLM proposes candidate edges from those events to existing vault pages; a senior engineer reviews and promotes a subset.
- **Blog 5 / 5.5 / 6** continue the promotion workflow as new evidence accumulates (surrogate model results, real site survey data, vendor RFQs).

Each post should contribute a fixed number of new candidate edges and a smaller number of edge promotions — the visible measure of "knowledge is compounding."

## Relationship to `scripts/wiki_graph_manifest.py`

The `wiki_graph_manifest.py` script (currently associated with Blog 2's static knowledge-graph figure) is a hand-curated subset of candidate edges that the author found visually informative for a specific figure. It is **not** a full export of the candidate graph and **not** a list of reviewed edges — it is a presentation artifact.

A future cleanup should:

- Replace `wiki_graph_manifest.py` with an automated export from the live vault frontmatter.
- Render two graph layers visually: candidate (faint) and reviewed (bold).
- Allow the figure to refresh as the vault grows.

## Current candidate edge count

(Approximate, derived from current vault frontmatter as of 2026-05-02:)

- 15 source-note pages × ~3 outbound edges each ≈ 45 edges
- 7 block pages × ~6 outbound edges each ≈ 42 edges
- 3 entity pages × ~5 outbound edges each ≈ 15 edges
- 2 concept pages + 1 synthesis × ~4 outbound edges each ≈ 12 edges
- **Total candidate edges ≈ 110–120; reviewed edges = 0.**

## Open questions for review

- Should candidate edges have a per-edge confidence score, or is "candidate or not" the only useful signal? v0 keeps it binary.
- Should the LLM be allowed to *propose* edges but not actually write them into frontmatter without a human nod? v0 lets the LLM write candidate edges directly because the alternative (human-in-the-loop on every edge) is too expensive at vault build-out time.
- How are reviewed edges actually stored — in the reviewed page's frontmatter, in a separate `reviewed_edges.yaml`, or both? v1 will pick one.

## Related

- [[reviewed_engineering_graph]] — the post-promotion view this page is the upstream of.
- [[governance_hierarchy]] — the underlying authority schema.
- [[behind_the_meter_siting]] — example of a concept page that aggregates candidate edges across the vault.
