# Phase A deployment runbook — run these on your Mac

**Goal:** ship the two Streamlit apps to Streamlit Cloud so Blog 1 can link to a live demo and Blog 2 has its own sizing playground.

Two apps ship in this pass:

| URL slug         | Entry point                                             | Purpose                     |
|------------------|---------------------------------------------------------|-----------------------------|
| `wwtp-demo`      | `stage1_5_wwtp_dc/app.py`                               | Blog 1 live demo            |
| `wwtp-sizing`    | `stage1_5_wwtp_dc/apps/blog2_sizing_app.py`             | Blog 2 sizing playground    |

---

## 1. Commit and push (Mac terminal)

```bash
cd ~/Desktop/LLM_Project/EnergyFlux

# Sanity check: you should see the files below as modified / untracked.
git status --short

# Commit 1 — deploy config (lean requirements.txt, streamlit theme,
#             runtime pin, committed demo CSVs, .gitignore exception rule).
git add .gitignore runtime.txt .streamlit/ \
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

git commit -m "feat(deploy): prep stage1_5 Streamlit app for Streamlit Cloud

- Split requirements.txt: lean runtime deps only (streamlit / pandas /
  numpy / plotly). Full simulation deps moved to requirements-dev.txt.
  Cold start ~15 s instead of ~3 min (qsdsan install avoidance).
- Add .streamlit/config.toml with blog-1 blue theme (#1F4E79, dark base).
- Pin Python 3.11 via runtime.txt for Streamlit Cloud.
- Whitelist 8 frozen demo CSVs in .gitignore; the deployed app reads
  these at load() time so they must ship with the repo."

# Commit 2 — Blog 2 parameterized sizing (design/ module + blog2 app + tests).
git add stage1_5_wwtp_dc/design/ \
        stage1_5_wwtp_dc/apps/ \
        stage1_5_wwtp_dc/tests/

git commit -m "feat(blog2): parametric sizing module + Blog 2 Streamlit app

- design/archetypes.py:  30/40/50/60 MGD WWTP presets with documented
                         engineering constants (PV density, PUE, rack kW,
                         tokens/s per MW, BESS duration, etc.).
- design/sizing.py:      pure size_site(name) -> dict. No I/O. Importable
                         as a tool by the future Gemma orchestrator.
- apps/blog2_sizing_app.py: Streamlit companion for Blog 2. Archetype
                         dropdown, live-updating KPIs, revenue chart at
                         four price points, cross-archetype comparison.
- tests/test_sizing.py:  regression pytest that locks the 30 MGD case to
                         Blog 1's published numbers and verifies metric
                         monotonicity across the four archetypes.

Leaves existing stage1_5_wwtp_dc/app.py and models/ untouched so Blog 3
and Blog 4 continue to build on the proven code path."

# Commit 3 (optional) — separately, if you want to keep the blog/ edits.
# If you don't want to commit the v20 blog updates yet, skip this.
# git add blog/
# git commit -m "docs(blog): iterate blog 1 v20 assets"

# Push to GitHub.
git push
```

---

## 2. Wire up Streamlit Cloud (browser)

Both apps live in the same repo; Streamlit Cloud lets you deploy more than one.

1. Go to **https://share.streamlit.io** and sign in with the GitHub account that owns `chennanli/EnergyFlux`.
2. Click **"New app"**.
3. For the **Blog 1 live demo**:
   - Repository: `chennanli/EnergyFlux`
   - Branch: `main` (or whatever your default is)
   - Main file path: `stage1_5_wwtp_dc/app.py`
   - Advanced settings → Python version: `3.11`
   - App URL (custom slug): `wwtp-demo` → final URL becomes `https://wwtp-demo.streamlit.app` (or suffixed if the slug is taken)
4. Click **Deploy**. First build takes 2–5 minutes. Watch the logs for import errors.
5. Click **"New app"** again for the **Blog 2 sizing app**:
   - Same repo and branch.
   - Main file path: `stage1_5_wwtp_dc/apps/blog2_sizing_app.py`
   - Python version: `3.11`
   - App URL: `wwtp-sizing` → `https://wwtp-sizing.streamlit.app`
6. Deploy. Same ~3 min build.

**Tip:** if a slug is taken, Streamlit Cloud will append `-chennanli` or a hash. Either is fine — capture the final URL and use it in the blog posts.

---

## 3. Smoke-test the deploys

Open each URL in a fresh browser window (not just a tab — avoids cached state) and check:

**`wwtp-demo` (Blog 1 live demo) checklist:**
- [ ] Page loads without red error banner
- [ ] "Grid Impact" tab: dual-line chart renders; 8,760-hr headline numbers populated
- [ ] "Full Year" tab: monthly stacked bars + solar-coverage bars + SOC heatmap all render
- [ ] "Three Scenarios" tab: Case 1 auto-expands with stacked-area chart

**`wwtp-sizing` (Blog 2 sizing) checklist:**
- [ ] Sidebar dropdown shows 4 archetypes
- [ ] Default (30 MGD) shows: `5,706 kWp` PV, `8.0 MWh` BESS, `2.00 MW` DC IT, `16 Racks`
- [ ] Revenue chart shows 4 bars, `$0.10 / M tok` bar lands around `$25.6 M`
- [ ] Switching dropdown to 60 MGD: PV jumps to `10,841 kWp`, revenue @ $0.30 to ~$146 M
- [ ] "Show every assumption" expander opens and shows 11 rows

If anything 404s or errors:
- Check Streamlit Cloud's build logs (available from the app's settings menu).
- Most common failure: Python version mismatch (force to 3.11 in advanced settings).
- Second most common: a CSV read returning None because the file wasn't committed — confirm with `git ls-tree HEAD stage1_5_wwtp_dc/data/`.

---

## 4. Plug the URLs back into the blog

Once both URLs are confirmed live, update:

1. `blog/github_pages/posts/01-ai-inference-buffers/index.html`
   - Add a "Live demo" link near the hero or in the footer.
2. The Medium post (via edit): add the same live-demo link at the bottom.
3. Update `README.md` at repo root with a "Live demos" section.

I can generate the exact HTML snippets once you send me the final URLs.

---

## 5. What happens next

After Phase A ships, we move to **Phase B — publish Blog 2**:
- Read `blog/Blog_2_Claude.docx`, `Blog_2_Codex.docx`, `Blog_2_Gemini_v2.docx`
- Merge best passages, check tone against Blog 1 v22
- Write `blog/blog2_v1.html` following the blog-1 GitHub Pages pattern
- Embed the `wwtp-sizing` URL as the interactive section
- Publish GitHub Pages first (canonical), then Medium with `rel=canonical`

Ping me when the deploy is green and I'll kick off Phase B.
