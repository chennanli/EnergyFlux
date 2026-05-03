"""Blog 2 Figure 3 — realistic PV tracker-farm layout for the default design.

Exports a standalone PNG (no Streamlit dependency) of the tracker farm
visualization used inside the Blog 2 flowsheet app's PV block editor.
Used as Fig 3 in the Blog 2 HTML post.

Usage:
    python scripts/build_blog2_fig3.py

Output:
    blog/_sources/blog2_fig3_pv_tracker_layout.png
"""
from __future__ import annotations

from pathlib import Path
import sys

# Make the package importable when running from repo root
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import plotly.io as pio

from stage1_5_wwtp_dc.apps.flowsheet.blocks import default_design, recompute_all
from stage1_5_wwtp_dc.apps.flowsheet.pv_layout_viz import build_tracker_farm_figure


OUTPUT_PATH = REPO_ROOT / "blog" / "_sources" / "blog2_fig3_pv_tracker_layout.png"


def main() -> int:
    # Build default design and compute outputs so the PV block has layout data
    design = recompute_all(default_design())

    # Render the tracker farm figure for the PV block
    fig = build_tracker_farm_figure(design["pv"], fig_height=500)

    # Export to PNG. plotly requires kaleido (or orca) for image export.
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        pio.write_image(fig, OUTPUT_PATH, width=1200, height=550, scale=2)
    except ValueError as e:
        print(f"[error] {e}")
        print()
        print("Plotly's PNG export needs the 'kaleido' package. Install it with:")
        print("   uv pip install kaleido")
        print("Or (if that fails due to ARM64 issues on Apple Silicon):")
        print("   uv pip install kaleido==0.2.1")
        return 1

    print(f"[write] {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    print(f"        {OUTPUT_PATH.stat().st_size / 1024:.0f} KB")

    # Also save an interactive HTML version for curious readers
    html_path = OUTPUT_PATH.with_suffix(".html")
    pio.write_html(fig, html_path, include_plotlyjs="cdn", full_html=True)
    print(f"[write] {html_path.relative_to(REPO_ROOT)}  (interactive version)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
