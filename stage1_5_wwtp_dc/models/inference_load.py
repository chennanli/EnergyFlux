"""Stage 1.5 — Inference data center load model.

Physical basis for flat load:
  A Token Plant sells inference API tokens 24/7. Inference hardware
  draws near-constant power regardless of time of day:
    - GPU-based systems at sustained high utilization: ~constant TDP
    - SRAM-based systems (Groq LPU, Cerebras WSE-3): SRAM must stay
      powered continuously; power is independent of token throughput

  Source: NVIDIA Tech Blog, March 24 2026
  "Scaling Token Factory Revenue and AI Efficiency by
   Maximizing Performance per Watt"
  URL: developer.nvidia.com/blog/scaling-token-factory-revenue-and
       -ai-efficiency-by-maximizing-performance-per-watt/

Energy verification:
  Flat DC 2,500 kW x 8,760 hr = 21,900 MWh/yr
  WWTP avg 2,500 kW x 8,760 hr = 21,900 MWh/yr
  Total facility               = 43,800 MWh/yr
  Solar generation (pvlib)     = 10,660 MWh/yr
  Solar self-sufficiency       = 10,660 / 43,800 = 24.3%
  This matches the white paper's stated 24% figure.

Token economics — Blackwell GB200 NVL72 baseline:
  5.8M tokens/sec/MW is derived from Blackwell GB200 NVL72 at ~125 kW/rack.
  Source A (throughput figure):
    Tom's Hardware, March 2025, Rubin Ultra / Kyber racks article
    "Nvidia is saying 5.8 million TPS per MW.
     With a single NVL72 using about 125kW..."
    URL: tomshardware.com/pc-components/gpus/
         nvidia-shows-off-rubin-ultra-with-600-000-watt-kyber-racks
         -and-infrastructure-coming-in-2027
  Source B (rack power confirmation):
    Supermicro GB200 NVL72 datasheet: "Operating Power 125kW to 135kW"
    URL: supermicro.com (search GB200 NVL72 datasheet)
  NOTE: 5.8M tok/s/MW has NOT been officially confirmed by NVIDIA
        for Vera Rubin NVL72. See README Hardware Basis for details.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

P_IT_MAX_KW   = 2000   # IT load: 16 racks x 125 kW/rack (Blackwell GB200)
P_DC_TOTAL_KW = 2500   # Facility DC load including cooling (PUE 1.25)

# Blackwell GB200 NVL72 baseline — media-derived figure, see docstring above
TOKENS_PER_SEC_PER_MW_BLACKWELL = 5.8e6


def generate_dc_load(hours: int = 8760, seed: int = 42) -> pd.DataFrame:
    """Return flat 2,500 kW DC load for all hours.

    Flat load is physically correct for a 24/7 inference Token Plant.
    Annual DC energy = 2,500 kW x 8,760 hr = 21,900 MWh/yr.
    Produces 24.3% solar self-sufficiency (consistent with white paper).

    The 'seed' parameter is accepted for API compatibility but unused.
    """
    return pd.DataFrame({
        "load_factor": np.ones(hours),
        "P_dc_kw":     np.full(hours, float(P_DC_TOTAL_KW)),
        "P_it_kw":     np.full(hours, float(P_IT_MAX_KW)),
    })
