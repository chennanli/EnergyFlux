"""Blog 2 Figure 1 — US WWTP size distribution + the AI-inference sweet spot.

Usage:
    python scripts/build_blog2_fig1.py

Two input modes (auto-detected):

* Mode A — if `stage1_5_wwtp_dc/data/external/epa_cwns/distribution_2022_raw.xlsx`
  or `...raw.csv` exists, aggregate the raw EPA CWNS Facility export into MGD bins.
* Mode B — otherwise, fall back to the bundled summary CSV
  (`distribution_2022_fallback.csv`) compiled from EPA CWNS 2022 published tables.

Outputs (written to `blog/_sources/`):

* `blog2_fig1_wwtp_distribution.png`  — the figure
* `blog2_fig1_data.csv`               — the bar data used (for reproducibility)

Design notes:

* We plot counts on a log Y-axis because the distribution is power-law-ish (a
  linear axis buries the 25–75 MGD band that we want to highlight).
* We add a cumulative-flow line on a secondary axis because "few plants
  contain most flow" is the contrarian observation the blog opens with.
* We shade the 25–75 MGD band in soft blue as the AI-inference sweet spot —
  that's the thesis anchor.
* Palette matches Blog 1 GitHub Pages blue (#1F4E79).
"""
from __future__ import annotations

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "stage1_5_wwtp_dc" / "data" / "external" / "epa_cwns"
OUTPUT_DIR = REPO_ROOT / "blog" / "_sources"

# Palette matches Blog 1 (GitHub Pages canonical, primaryColor #1F4E79).
BLOG1_BLUE = "#1F4E79"
BLOG1_BLUE_LIGHT = "#4A78A8"
# Gold gradient for the three "viable" bins: 25-75 (brightest), 75-150, >=150.
SWEET_SPOT_25_75   = "#E8A33D"   # volume sweet spot
FLAGSHIP_75_150    = "#E8B870"   # flagship tier
METRO_150_PLUS     = "#E8CFA3"   # metro anchor
ACCENT_LINE = "#C94B4B"
BAR_GRAY = "#9AA6B2"


# ---------------------------------------------------------------------------
# Mode A — aggregate raw EPA CWNS Facility export into MGD bins
# ---------------------------------------------------------------------------
def _try_aggregate_raw(dir_: Path) -> pd.DataFrame | None:
    """Return aggregated distribution DF if a raw EPA CWNS export is present.

    The EPA CWNS Facility export typically has columns like
    ``FACILITY_ID``, ``DESIGN_FLOW_MGD``, ``FACILITY_TYPE``. We filter to
    public POTWs and bin by design flow.
    """
    candidates = [
        dir_ / "distribution_2022_raw.xlsx",
        dir_ / "distribution_2022_raw.csv",
    ]
    raw_path = next((p for p in candidates if p.exists()), None)
    if raw_path is None:
        return None

    print(f"[Mode A] Aggregating raw EPA CWNS export at {raw_path.name} ...")

    if raw_path.suffix == ".xlsx":
        df = pd.read_excel(raw_path)
    else:
        df = pd.read_csv(raw_path)

    # EPA CWNS column naming varies between releases; be lenient.
    flow_col = next(
        (c for c in df.columns if "DESIGN_FLOW" in c.upper() or "DESIGN FLOW" in c.upper()),
        None,
    )
    if flow_col is None:
        print("[Mode A] ERROR: could not find a DESIGN_FLOW column in the raw "
              "export. Columns:", df.columns.tolist())
        return None

    df = df.dropna(subset=[flow_col]).copy()
    df[flow_col] = pd.to_numeric(df[flow_col], errors="coerce")
    df = df.dropna(subset=[flow_col])

    bins = [0, 1, 10, 25, 75, 150, 10_000]
    labels = ["<1 MGD", "1-10 MGD", "10-25 MGD", "25-75 MGD", "75-150 MGD", ">=150 MGD"]
    df["bin"] = pd.cut(df[flow_col], bins=bins, labels=labels, right=False)

    counts = df.groupby("bin", observed=True).size().reset_index(name="plant_count")
    flows = df.groupby("bin", observed=True)[flow_col].sum().reset_index(name="total_flow_mgd")
    agg = counts.merge(flows, on="bin")
    agg["share_of_plants_pct"] = agg["plant_count"] / agg["plant_count"].sum() * 100
    agg["cumulative_flow_share_pct"] = (
        agg["total_flow_mgd"].cumsum() / agg["total_flow_mgd"].sum() * 100
    )
    agg = agg.rename(columns={"bin": "bin_label"})
    agg["bin_label"] = agg["bin_label"].astype(str)

    # Backfill numeric low/high for downstream consumers.
    bin_bounds = {
        "<1 MGD": (0.0, 1.0),
        "1-10 MGD": (1.0, 10.0),
        "10-25 MGD": (10.0, 25.0),
        "25-75 MGD": (25.0, 75.0),
        "75-150 MGD": (75.0, 150.0),
        ">=150 MGD": (150.0, 500.0),
    }
    agg["bin_low_mgd"] = agg["bin_label"].map(lambda b: bin_bounds[b][0])
    agg["bin_high_mgd"] = agg["bin_label"].map(lambda b: bin_bounds[b][1])

    print(f"[Mode A] Aggregated {df.shape[0]:,} facilities into "
          f"{agg.shape[0]} size bins.")
    return agg


# ---------------------------------------------------------------------------
# Mode B — read bundled summary CSV
# ---------------------------------------------------------------------------
def _load_fallback(dir_: Path) -> pd.DataFrame:
    path = dir_ / "distribution_2022_fallback.csv"
    print(f"[Mode B] Using bundled summary table at {path.name} "
          f"(EPA CWNS 2022, Table 2-3 + NACWA validation).")
    return pd.read_csv(path)


# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------
def build_figure(df: pd.DataFrame, out_png: Path) -> None:
    fig, ax_count = plt.subplots(figsize=(11.0, 5.6), dpi=150)

    x = np.arange(len(df))
    viable_palette = {
        "25-75 MGD":   SWEET_SPOT_25_75,
        "75-150 MGD":  FLAGSHIP_75_150,
        ">=150 MGD":   METRO_150_PLUS,
    }
    bar_colors = [
        viable_palette.get(row.bin_label, BAR_GRAY)
        for row in df.itertuples()
    ]

    bars = ax_count.bar(
        x,
        df["plant_count"],
        color=bar_colors,
        edgecolor="white",
        linewidth=1.2,
        zorder=3,
    )

    # Count labels on top of each bar.
    for rect, n in zip(bars, df["plant_count"]):
        ax_count.text(
            rect.get_x() + rect.get_width() / 2,
            rect.get_height() * 1.08,
            f"{int(n):,}",
            ha="center", va="bottom",
            fontsize=10, color="#333", zorder=4,
        )

    ax_count.set_yscale("log")
    # Extra headroom above max bar so the "Viable band" bracket has room.
    ax_count.set_ylim(5, df["plant_count"].max() * 8)
    ax_count.set_ylabel("Number of US public WWTPs (log scale)",
                        color=BLOG1_BLUE, fontsize=12)
    ax_count.tick_params(axis="y", colors=BLOG1_BLUE)
    ax_count.set_xticks(x)
    ax_count.set_xticklabels(df["bin_label"], fontsize=11)
    ax_count.set_xlabel("Plant design flow", fontsize=12)
    ax_count.grid(axis="y", alpha=0.25, zorder=0)
    ax_count.set_axisbelow(True)

    # Cumulative flow share on secondary axis.
    ax_cum = ax_count.twinx()
    ax_cum.plot(
        x,
        df["cumulative_flow_share_pct"],
        marker="o", markersize=8,
        linewidth=2.5, color=ACCENT_LINE,
        zorder=5,
        label="Cumulative share of US wastewater flow",
    )
    for xi, v in zip(x, df["cumulative_flow_share_pct"]):
        ax_cum.text(
            xi, v + 3, f"{v:.0f}%",
            ha="center", va="bottom", fontsize=9,
            color=ACCENT_LINE, zorder=6,
        )
    ax_cum.set_ylim(0, 112)
    ax_cum.set_ylabel("Cumulative share of total flow (%)",
                      color=ACCENT_LINE, fontsize=12)
    ax_cum.tick_params(axis="y", colors=ACCENT_LINE)
    ax_cum.grid(False)

    # Annotate the three-tier viable band.
    viable_bins = ["25-75 MGD", "75-150 MGD", ">=150 MGD"]
    viable_idx = [df.index[df["bin_label"] == b].tolist() for b in viable_bins]
    viable_idx = [v[0] for v in viable_idx if v]
    if viable_idx:
        i_left = viable_idx[0]
        i_right = viable_idx[-1]
        y_band = df["plant_count"].max() * 3.5

        ax_count.annotate(
            "", xy=(i_left - 0.35, y_band), xytext=(i_right + 0.35, y_band),
            arrowprops=dict(arrowstyle="|-|", color=SWEET_SPOT_25_75, lw=1.5),
        )
        ax_count.text(
            (i_left + i_right) / 2, y_band * 1.25,
            "Viable band — 25 MGD and up",
            ha="center", va="bottom",
            fontsize=10.5, fontweight="bold", color=SWEET_SPOT_25_75,
        )

        # Sub-labels under each tier
        i = df.index[df["bin_label"] == "25-75 MGD"].tolist()
        if i:
            ax_count.text(
                i[0], df.loc[i[0], "plant_count"] / 2.2,
                "volume\nsweet spot",
                ha="center", va="center",
                fontsize=9, fontweight="bold", color="#5a3d10",
            )
        i = df.index[df["bin_label"] == "75-150 MGD"].tolist()
        if i:
            ax_count.text(
                i[0], df.loc[i[0], "plant_count"] / 2.2,
                "flagship\ntier",
                ha="center", va="center",
                fontsize=9, fontweight="bold", color="#5a3d10",
            )
        i = df.index[df["bin_label"] == ">=150 MGD"].tolist()
        if i:
            ax_count.text(
                i[0], df.loc[i[0], "plant_count"] / 2.2,
                "metro\nanchor",
                ha="center", va="center",
                fontsize=9, fontweight="bold", color="#5a3d10",
            )

    # Title + subtitle
    fig.suptitle(
        "US wastewater plant size is power-law — and everything above 25 MGD is behind-the-meter AI territory",
        fontsize=13, fontweight="semibold", color=BLOG1_BLUE, y=0.98,
    )
    ax_count.set_title(
        "~350 plants (2.3% of the count) process 52% of national flow. "
        "25–75 MGD is the volume sweet spot; 75–150 MGD supports flagship 6–15 MW DCs; "
        "metro plants (≥150 MGD) host 15+ MW anchor campuses.",
        fontsize=9.5, color="#555", pad=12,
    )

    # Source line
    total = int(df["plant_count"].sum())
    fig.text(
        0.01, 0.01,
        f"Source: EPA Clean Watersheds Needs Survey 2022 (Table 2-3, aggregated). "
        f"n = {total:,} US public POTWs.",
        ha="left", va="bottom", fontsize=8, color="#777",
    )

    plt.tight_layout(rect=(0, 0.04, 1, 0.95))
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[write] {out_png.relative_to(REPO_ROOT)}")


# ---------------------------------------------------------------------------
# Entry
# ---------------------------------------------------------------------------
def main() -> int:
    df = _try_aggregate_raw(DATA_DIR)
    if df is None:
        df = _load_fallback(DATA_DIR)

    # Normalize column order for downstream consumers.
    cols = ["bin_label", "bin_low_mgd", "bin_high_mgd",
            "plant_count", "share_of_plants_pct", "cumulative_flow_share_pct"]
    df = df[[c for c in cols if c in df.columns]].copy()

    # Write machine-readable version alongside the PNG.
    csv_out = OUTPUT_DIR / "blog2_fig1_data.csv"
    png_out = OUTPUT_DIR / "blog2_fig1_wwtp_distribution.png"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_out, index=False)
    print(f"[write] {csv_out.relative_to(REPO_ROOT)}")

    build_figure(df, png_out)
    print("done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
