# AGENTS.md — vault rules for AI agents

This file applies to **every AI agent that reads or writes this vault** —
Claude (any version), Codex, future agents, or any other LLM running under
human direction. It supersedes any conflicting instructions an agent may
have received elsewhere when those instructions concern this vault.

`CLAUDE.md` (the schema and operating manual for this vault) remains in
place; this file enumerates the **rules** an agent must follow on top of
that schema.

---

## Eight rules

### 1. `raw/` is immutable

`raw/` (everything under `knowledge_vault/raw/`) holds source documents:
imported papers, articles, datasets, vendor PDFs, the legacy
`wiki_legacy/` files. These are never edited, renamed, or deleted by an
agent. If a source needs correction, the corrected version is added as a
new file at a new path, and the new path is referenced from a new wiki
page.

### 2. `wiki/` is the maintained layer

Every page in `wiki/` has YAML frontmatter, a section structure, and a
declared authority level. Agents may add to `wiki/`, edit pages where the
new content is consistent with the authority level, and create new pages
following the templates in `templates/`.

Agents may **never** raise a page's authority level on their own — that
is reserved for human review (see rule 4).

### 3. Candidate cannot be cited as fact

Pages and edges at `authority: candidate` (and `legacy`, treated the same
way for citation purposes) cannot be cited as fact by the AI assistant or
in any downstream artifact. They may be surfaced in answers, but every
chain that depends on them must be tagged "pending review" in the user-
facing output.

### 4. Reviewed and authoritative are the only primary citations

Pages and edges at `authority: reviewed` or `authority: authoritative` may
be cited as fact in engineering recommendations, blog content, and
assistant answers. Agents producing such citations must include the page
title and authority level in the cited reference.

### 5. Promotion requires explicit human approval

The transition from `candidate` → `reviewed` (or `legacy` → any higher
level) is **always** human-mediated. The mechanism is a Git pull request
that updates `approved_by` and `approved_date` in the page frontmatter,
merged by a designated maintainer. An agent may propose a promotion (in a
PR description, in conversation, in the log), but cannot commit the
promotion itself.

### 6. Scope prevents cross-domain overgeneralization

Every page declares its `scope:` (host_type, region, equipment,
voltage_level, applies_when). Authority alone is not sufficient to use a
page in a downstream answer — the page's scope must overlap with the
question's scope. An ERCOT BTM lesson is not safe to apply in CAISO; an
LFP BESS heuristic is not safe to apply to NMC. Agents must check scope
before citing, and tag any extrapolation as a scope-mismatch in the
answer.

### 7. `log.md` must be updated

Every operation that changes the vault — ingest of a new source, creation
of a new page, edit to an existing page, query that produced a new
synthesis, lint pass, promotion, supersession — must append an entry to
`log.md` with the absolute date+time, operation type, and a one-paragraph
description. The log is append-only and is the audit trail for governance
review.

### 8. `index.md` must stay current

`index.md` is the navigational catalog of the vault. Every new page must
appear in `index.md` under the appropriate section (Sources / Blocks /
Graphs / Concepts / Entities / Synthesis), with its authority level
visible. When a page's authority level changes, the index entry updates.

---

## Operating notes

- **Default authority for newly-created pages is `candidate`.** Pages
  imported from earlier work may be marked `legacy`. Agents must never
  set `reviewed` or `authoritative` on creation.
- **Templates live in `templates/`.** When creating a new page, copy the
  appropriate template (`entity_template.md`, `source_template.md`,
  `concept_template.md`, `synthesis_template.md`) and fill in the
  frontmatter and section bodies. Do not invent new sections; the
  templates are the contract.
- **Wikilinks (`[[target]]`) create candidate edges in the graph.** See
  `wiki/graphs/ai_candidate_graph.md` for what that means.
- **Voice convention:** plain prose, sparingly bulleted, no emoji unless
  in user-facing UI. Numbers carry units. Citations name the page title
  and authority level.
- **When in doubt, ask.** An agent that is unsure whether a citation is
  supported, a scope is appropriate, or a promotion is justified must
  surface the uncertainty rather than guess.

## Tooling that enforces these rules

- `design/rag_v2.py` reads frontmatter and filters by authority.
- `scripts/build_wiki.py` renders pages with authority badges and scope
  strips so reviewers can see governance state at a glance.
- `apps/blog2_genai_app_v2.py` shows the authority badge on every cited
  hit and tags candidate/legacy citations as "pending review."

## Relationship to `CLAUDE.md`

`CLAUDE.md` is the **schema** — what fields exist, what sections each
page type has, how the LLM should be invoked.

`AGENTS.md` (this file) is the **rules** — what agents may and may not do
when operating on the vault.

If the two conflict, `AGENTS.md` wins for any rule about authority,
promotion, scope, or audit trail; `CLAUDE.md` wins for any rule about
schema, sections, or tooling invocation. In practice the two are aligned;
if you find a real conflict, raise it.
