# Vault log

Append-only chronological record of vault operations. Each entry starts with `## [YYYY-MM-DD HH:MM] <op> | <subject>` so it parses with `grep '^## \['`.

Operations: `ingest`, `query`, `lint`, `promote`, `supersede`, `setup`.

---

## [2026-05-02 10:30] setup | Vault scaffolded

Initial scaffolding: vault schema doc (internal schema file, not included in the public mirror), `README.md`, `index.md`, `log.md`, raw/wiki/templates directory tree. Bootstrap content seeded with three example entity pages (`bess_4hr_lfp`, `gb200_nvl72`, `wwtp_45mgd_archetype`), two concept pages (`behind_the_meter_siting`, `governance_hierarchy`), and one synthesis page (`syn_btm_siting_cases`). All seeded pages are at `authority: candidate` or `authority: legacy` pending Chennan's review.

The legacy `stage1_5_wwtp_dc/design_wiki/` 15 markdown files are imported into `raw/wiki_legacy/` as immutable raw sources, not as wiki pages. They will be re-ingested into the wiki/ layer over time, on demand.

This vault runs in parallel to the simplified RAG that powers the published Blog 2 copilot. Migration of the copilot to retrieve from this vault is not on the immediate roadmap; this vault is for ongoing engineering work and growth.

---

## [2026-05-02 11:15] ingest | Source pages from legacy raw

Created two source-level pages summarizing the most-cited legacy raws so they have a citable wiki location:

- `wiki/sources/src_legacy_4h_battery_standard.md` — points back to `raw/wiki_legacy/4_hour_battery_standard.md`. Authority `legacy` because the underlying file was promoted to "design standard" in the legacy folder without an external citation; needs re-grounding to NREL ATB or vendor spec before promotion to `reviewed`.
- `wiki/sources/src_legacy_blackwell_gb200_nvl72.md` — points back to `raw/wiki_legacy/blackwell_gb200_nvl72.md`. Authority `legacy` for the same reason; needs cross-check against NVIDIA datasheets.

Index updated. No entity or concept page changed.

---

## [2026-05-02 11:25] setup | Templates added

Created `templates/entity_template.md`, `templates/source_template.md`, `templates/concept_template.md`, `templates/synthesis_template.md`. These match the four `wiki/` subdirectories. The LLM maintainer should copy a template when adding a new page rather than writing the YAML frontmatter from memory.

---

## [2026-05-02 11:40] query | Demo: "Why did the 45 MGD WWTP archetype land on 21 racks of GB200?"

**Question.** Walk me through, from this vault, why the worked Blog 2 WWTP archetype lands on 21 racks of GB200 NVL72 and a 4 MVA → upgraded transformer.

**Answer (composed by reading the vault):**

The 21-rack number falls out of the per-rack facility draw and the chosen DC budget. From [[gb200_nvl72]]: each rack is rated at **~125 kW** facility load (NVIDIA spec: 120 kW typical, 132 kW peak; design to 125 kW). The Blog 2 worked case sets the AI factory's nameplate at **2.62 MW DC** for the 45 MGD archetype. 2,620 kW ÷ 125 kW per rack ≈ **21 racks**. (Source: [[wwtp_45mgd_archetype]], headline parameters block; cross-checked against [[src_legacy_blackwell_gb200_nvl72]] which cites the 125 kW figure to NVIDIA GB200 NVL72 product brief, Feb 2024.)

The 4 MVA transformer reasoning is structural, not arbitrary. The WWTP itself peaks at ~3,750 kW (aeration + pumping + ancillaries for a 25–60 MGD plant). U.S. utility convention sizes the service transformer at roughly 1.07× to 1.4× peak; the lean end is 1.07× → 4 MVA. (Source: [[wwtp_45mgd_archetype]] honest-scope-limits block.) The new AI factory load (4,578 kW worst-case-simultaneity) plus the WWTP baseline exceeds 4 MVA, so the worked case requires a transformer upgrade. (Source: same page.)

**Authority profile of the answer:**
- Per-rack draw → cited from a `legacy` source page that traces to NVIDIA's primary doc — treat as authoritative for the magnitude, candidate for the specific 125 kW design-point.
- Transformer sizing convention (1.07–1.4× peak) → currently `candidate` in [[wwtp_45mgd_archetype]]; needs grounding to IEEE C57.92 or equivalent before promotion to `reviewed`.
- 21-rack count → arithmetic, not a citable claim.

**Scope check.** The question is in scope for `host_type: WWTP, voltage_level: distribution / behind_the_meter, applies_when: 25–150 MGD mid-size`. No scope mis-application.

**What this query did not find.** No primary-source IEEE/ANSI citation for the transformer sizing convention exists in this vault yet. That is a known gap and is in the open-questions list on [[wwtp_45mgd_archetype]].

---

## [2026-05-02 11:55] lint | First-pass lint of vault as of 11 pages

Ran a manual lint pass over the 11 wiki pages and 21 raw files. Findings:

**L-1 (real contradiction, severity: medium).** [[gb200_nvl72]] §"Why this is the default" says: *"For a 2 MW DC budget at the worked-case 30 MGD WWTP archetype, the rack count is straightforward: 2 MW / 125 kW per rack ≈ 16 racks (the headline number used throughout the EnergyFlux stage 1.5 simulation). Scaling to 45 MGD and 2.62 MW DC gives 21 racks."* This refers to a "30 MGD worked case" that no longer exists — the archetype was renamed to 45 MGD ([[wwtp_45mgd_archetype]]). The 30 MGD framing is residual from the stage 1.5 simulation and the legacy source page [[src_legacy_blackwell_gb200_nvl72]] which still cites the 30 MGD number. **Resolution:** the 30 MGD reference in [[gb200_nvl72]] should be moved to a "history note" subsection or replaced with the 45 MGD framing directly. Logged for next ingest pass; not auto-fixing because the wording choice is editorial.

**L-2 (orphan, severity: low).** No PV entity page exists yet, but [[wwtp_45mgd_archetype]] references PV via `informs: [pv]` and includes a PV nameplate of 7,474 kWp. **Resolution:** create `wiki/entities/pv_single_axis_bifacial.md` from `raw/wiki_legacy/pv/single_axis_tracker.md` and `bifacial_gain.md` to give the PV reference a target. Deferred — known gap.

**L-3 (incomplete approval metadata, severity: low).** All `legacy` pages have `approved_by: null` and `approved_date: null`, which is correct *as legacy* but means none of them can be cited as `reviewed` until they go through the promotion workflow. This is by design (see [[governance_hierarchy]]); the lint surfaces it so the count is visible: **5 pages in legacy/candidate state, 0 in reviewed, 0 in authoritative**. Tracking metric.

**L-4 (informs-block underspecified, severity: low).** [[behind_the_meter_siting]] declares `informs: [grid, wwtp, rack, bess, pv]` — five blocks. The current vault has entity pages for three (`bess_4hr_lfp`, `gb200_nvl72`, `wwtp_45mgd_archetype`) plus the BTM concept itself. PV and grid blocks have no entity pages yet. Not a contradiction; a gap. Captured for future ingest.

**L-5 (no contradictions found between primary and synthesized layers).** Spot-checked: the 4-hour BESS standard claim, the 125 kW per-rack draw claim, and the 23-acre buffer assumption are all consistent between the source page and the entity page that synthesizes from it.

**L-6 (no broken wikilinks).** Every `[[...]]` reference points to a file that exists in `wiki/`.

**Summary.** One real contradiction (L-1, residual 30 MGD framing in gb200_nvl72), four gaps (L-2, L-3, L-4, plus more lint passes needed when the vault grows), no broken links. The vault is clean enough to be useful but has the shape of an early-stage project — most pages are `candidate` or `legacy` and need promotion work before they can be auto-cited.

---

## [2026-05-02 12:00] supersede | L-1 fix in [[gb200_nvl72]]

Resolved L-1 from the 11:55 lint pass. Edited [[gb200_nvl72]] §"Why this is the default for design-stage sizing" to use the 45 MGD archetype as the worked case directly, with the historic 30 MGD / 16-rack number explicitly framed as preserved-for-traceability via [[src_legacy_blackwell_gb200_nvl72]]. Frontmatter `last_lint_fix` field added.

This is a `supersede` operation in the sense that it replaces wording inside an existing page, not the page itself. No `supersedes:` link was set because the page identity is unchanged.

---

## [2026-05-02 14:30] hardening | Vault hardening pass v0.1

Per user instruction (governed-knowledge-vault hardening pass), this session expanded the vault from 8 thin pages to 30 structured pages with strict template compliance, governance documentation, and an honest authority audit.

**What was added:**

- 13 new source notes under `wiki/sources/` — one per legacy md not previously synthesized: `src_legacy_amd_mi300x`, `src_legacy_bess_nrel_atb_2024`, `src_legacy_bifacial_gain`, `src_legacy_cerebras_wse3`, `src_legacy_dc_industry_benchmarks`, `src_legacy_dual_axis`, `src_legacy_fixed_tilt`, `src_legacy_pv_lazard_lcoe_2024`, `src_legacy_single_axis_tracker`, `src_legacy_tou_arbitrage`, `src_legacy_tx_ercot_interconnect`, `src_legacy_vera_rubin_nvl144`, `src_legacy_wwtp_buffer_setback`. Total source notes now 15 (3 existing + 12 new — `src_legacy_tou_arbitrage` was started earlier this session and rewritten under the new template).
- 7 block pages under new `wiki/blocks/` directory: `pv_array`, `inverter`, `bess`, `dc_bus`, `ai_racks`, `wwtp_load`, `service_transformer`. Each follows the strict 7-question structure: what the block represents, key sizing variables, upstream dependencies, downstream dependencies, source notes that inform it, candidate assumptions pending review, what would make it authoritative/reviewed.
- 2 graph concept pages under new `wiki/graphs/` directory: `ai_candidate_graph` (LLM-proposed edges, not facts) and `reviewed_engineering_graph` (human-approved edges, the only edges the AI assistant may cite as fact). Promotion workflow documented.
- `AGENTS.md` at vault root: 8 governance rules for any AI agent operating on the vault. Distinct from the vault schema doc (internal schema file, not included in the public mirror).

**What was rewritten:**

- 3 existing source notes (`src_legacy_4h_battery_standard`, `src_legacy_blackwell_gb200_nvl72`, `src_legacy_tou_arbitrage`) reformatted to the strict 6-section template: Source Summary, Key Claims, Engineering Use, Limitations, Related, Informs.
- `index.md` rewritten with six sections (Sources / Blocks / Graphs / Concepts / Entities / Synthesis), each entry showing authority level. Honest top-line stats (0 reviewed, 0 authoritative, 13 candidate, 14 legacy).

**What was NOT done (deliberately):**

- **No page was promoted from candidate or legacy to reviewed or authoritative.** This was an explicit constraint. Promotion requires human approval, which has not happened. Every page in the vault is at candidate or legacy authority level.
- **No edges were promoted from the candidate graph to the reviewed graph.** Same reason.
- **`stage1_5_wwtp_dc/design_wiki/` was not deleted.** The 15 legacy markdown files remain in place. Only `design_wiki/README.md` was added (in a prior session) pointing to the vault. The legacy v1 retriever (`design/rag.py`) and v1 Streamlit app (`apps/blog2_genai_app.py`) continue to function unchanged.

**Authority audit (post-hardening):**

- Authoritative: 0
- Reviewed: 0
- Candidate: 14 (3 entities, 7 blocks, 2 graphs, 1 synthesis, 1 concept — was 5 before this pass)
- Legacy: 16 (15 source notes + 1 governance-hierarchy concept page)
- Total wiki pages: **30**

The vault is now structurally complete enough that a reader who clicks through it can understand: what each block does, where its assumptions come from, what's still pending review, and how the candidate→reviewed promotion is supposed to work. None of that yet means anything is **reviewed** — that is the next stage of work, requiring senior-engineer time per page, not a one-shot agent pass.

---

*Future entries appended below by the LLM maintainer.*
