# EPA Clean Watersheds Needs Survey (CWNS) — WWTP size distribution

## What we need from you (one-time, ~5 minutes)

The script `scripts/build_blog2_fig1.py` can run in two modes:

### Mode A (preferred) — use the official EPA CWNS 2022 dataset

1. Go to https://ordsext.epa.gov/cwns/apexpages.cwns2022_data and download the **Facility** data export (CSV or Excel).
2. Save it as `distribution_2022_raw.xlsx` (or `.csv`) in this folder.
3. The script will aggregate by design flow into MGD bins and write `distribution_2022.csv`.

The EPA CWNS data is public-domain, refreshed every ~4 years. The 2022 release is the current one as of April 2026.

### Mode B (fallback) — use the bundled summary table

If you don't want to hit the EPA data portal, the script auto-uses `distribution_2022_fallback.csv` in this folder. Those numbers are hand-compiled from:

* EPA CWNS 2022 Summary of Results report, Table 2-3 (design flow distribution)
* 40 CFR § 35.2005 POTW size tier definitions
* NACWA 2022 Financial Survey (secondary validation)

The fallback CSV is **already committed** to the repo so the figure can build in CI without external downloads.

## What gets produced

`scripts/build_blog2_fig1.py` writes **two** artifacts to `blog/_sources/`:

* `blog2_fig1_wwtp_distribution.png` — the figure for Blog 2's opening hook
* `blog2_fig1_data.csv` — machine-readable version of the bar data, for anyone who wants to reproduce

Run from repo root:

```bash
python scripts/build_blog2_fig1.py
```

## What the figure shows

X-axis: plant size bins (< 1 MGD, 1–10, 10–25, 25–75, 75–150, ≥ 150).
Y-axis (primary): count of US public WWTPs in each bin (log scale).
Y-axis (secondary, line): cumulative share of total treated flow.
Highlight: the **25–75 MGD band** shaded as the "AI-inference-economic sweet spot" (enough load + buffer land to amortize a 2–5 MW colocated DC).

## Licensing

EPA CWNS data is produced with federal funds; it is in the public domain in the United States under 17 USC § 105.
