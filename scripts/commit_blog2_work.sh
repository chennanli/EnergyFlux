#!/bin/bash
# One-shot script to commit the Blog 2 work as 5 clean logical commits.
#
# Run on your Mac:
#   cd ~/Desktop/LLM_Project/EnergyFlux
#   bash scripts/commit_blog2_work.sh
#
# Safe to run: every step is shown before it runs, and the script aborts
# on any error. API keys are pre-scanned before commits. .env is gitignored.

set -e  # abort on any error

echo "════════════════════════════════════════════════════════════"
echo "  EnergyFlux — Blog 2 commit script"
echo "════════════════════════════════════════════════════════════"
echo

# ── Step 0: safety — scan for any leaked API keys in tracked files ────────
echo "🔍 Step 0/6 — Scanning for leaked API keys in source…"
LEAKS=$(grep -rE '(nvapi-[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9]{20,})' \
    --include='*.py' --include='*.md' --include='*.toml' \
    --include='*.txt' --include='*.html' --include='*.yml' \
    --include='*.json' --include='*.sh' \
    . 2>/dev/null || true)
if [ -n "$LEAKS" ]; then
    echo
    echo "❌ ABORTING — found something that looks like an API key:"
    echo "$LEAKS"
    echo
    echo "Remove these strings from source before committing."
    exit 1
fi
echo "   ✓ clean"
echo

# ── Step 1: docs/planning ──────────────────────────────────────────────────
echo "📝 Step 1/6 — docs commit (roadmap + study plan + PRDs)…"
git add ROADMAP.md STUDY_PLAN.md CAREER_TARGETING.md BLOG2_PRD.md DEPLOY_RUNBOOK.md
git commit -m "docs: EnergyFlux roadmap + study plan + Blog 2 PRD

- ROADMAP.md  — 10-post publishing arc with Pioneer/Medium/Slow tiers
- STUDY_PLAN.md  — 8-phase learn+build sequence (Python thermal, EnergyPlus,
                   Modelica, pandapower grid-to-chip, surrogate models)
- CAREER_TARGETING.md  — NVIDIA SA positioning + Genesis Mission alignment
- BLOG2_PRD.md  — Blog 2 MVP scope + acceptance criteria
- DEPLOY_RUNBOOK.md  — Streamlit Cloud deploy procedure"
echo "   ✓ committed"
echo

# ── Step 2: deploy prep + lean requirements split ─────────────────────────
echo "🚀 Step 2/6 — deploy config commit…"
git add .gitignore .streamlit/ runtime.txt \
        stage1_5_wwtp_dc/__init__.py \
        stage1_5_wwtp_dc/requirements.txt \
        stage1_5_wwtp_dc/requirements-dev.txt \
        stage1_5_wwtp_dc/data/case1_results.csv \
        stage1_5_wwtp_dc/data/case2_results.csv \
        stage1_5_wwtp_dc/data/case3_results.csv \
        stage1_5_wwtp_dc/data/dispatch_hourly.csv \
        stage1_5_wwtp_dc/data/pv_hourly.csv \
        stage1_5_wwtp_dc/data/powerflow_hourly.csv \
        stage1_5_wwtp_dc/data/wwtp_load_hourly.csv \
        stage1_5_wwtp_dc/data/wwtp_load_shifted_do.csv
git commit -m "feat(deploy): Streamlit Cloud prep + lean requirements

Split requirements.txt into runtime-only (streamlit, pandas, numpy, plotly,
matplotlib, openai, python-dotenv) and requirements-dev.txt (full simulation:
pvlib, qsdsan, pandapower, scipy). Cold start on Streamlit Cloud drops from
~3 min to ~15 s.

Whitelist 8 frozen demo CSVs in .gitignore so the deployed app can read
them at startup."
echo "   ✓ committed"
echo

# ── Step 3: Blog 2 sizing engine (physics + wiki + RAG + LLM) ─────────────
echo "🧠 Step 3/6 — sizing engine + design wiki + NIM integration commit…"
git add stage1_5_wwtp_dc/design/ \
        stage1_5_wwtp_dc/design_wiki/ \
        stage1_5_wwtp_dc/tests/
git commit -m "feat(blog2): parametric sizing engine + design wiki + NIM integration

- design/archetypes.py + sizing.py  — pure functions: 30/40/50/60 MGD presets
                                      -> full site sizing report
- design/pv_tools.py  — pvlib-style wrappers (design_pv_array,
                        calc_annual_yield, compare_pv_technologies)
- design/rag.py  — TF-IDF retrieval over 15-file design_wiki, FAISS-ready
- design/llm.py  — NVIDIA NIM client + tool-calling loop
- design_wiki/  — 15 Karpathy-style md entries (hardware, PV, BESS,
                  regulations, CAPEX) with source citations
- tests/  — 36 regression assertions locking the Blog 1 headline numbers"
echo "   ✓ committed"
echo

# ── Step 4: Blog 2 Figure 1 ───────────────────────────────────────────────
echo "📊 Step 4/6 — Blog 2 Figure 1 (EPA WWTP distribution) commit…"
# blog/ is in .gitignore per the Blog 1 workflow — force-add the specific
# artifacts we want to publish.
git add scripts/build_blog2_fig1.py scripts/commit_blog2_work.sh
git add -f blog/_sources/blog2_fig1_wwtp_distribution.png \
           blog/_sources/blog2_fig1_data.csv
git commit -m "feat(blog2): Figure 1 — US WWTP size distribution

EPA CWNS 2022 aggregated by size bin. Highlights the 25-150 MGD 'viable
band' (3-tier gold gradient) where AI-inference colocation pencils out.
Fallback CSV bundled; raw EPA export auto-detected if present."
echo "   ✓ committed"
echo

# ── Step 5: Blog 2 demo apps ──────────────────────────────────────────────
echo "🎨 Step 5/6 — Blog 2 demo apps (chat + flowsheet) commit…"
git add stage1_5_wwtp_dc/apps/
git commit -m "feat(blog2): two demo apps — chat UI + flowsheet UI

- apps/blog2_sizing_app.py  — simple dropdown archetype picker
- apps/blog2_genai_app.py  — chat-first: LLM drives, tools + wiki citations
- apps/blog2_flowsheet_app.py  — flowsheet-first: engineer clicks blocks,
                                 live recompute, LLM copilot in sidebar
- apps/flowsheet/  — block-based engine (blocks, canvas, editors,
                     pv_layout_viz, copilot)

Paradigm: Aspen/ETAP-style flowsheet with Plotly canvas, click-to-edit
blocks, and LLM demoted to sidebar assistant."
echo "   ✓ committed"
echo

# ── Step 6: show summary + prompt to push ─────────────────────────────────
echo "📋 Step 6/6 — summary"
echo "────────────────────────────────────────────────────────────"
git log --oneline -6
echo "────────────────────────────────────────────────────────────"
echo
echo "✅ Five commits created. NOT yet pushed to origin."
echo
echo "Review the log above. When happy, push with:"
echo "   git push"
echo
echo "Or if something looks wrong, undo all 5 commits (keeps files):"
echo "   git reset --soft HEAD~5"
echo
