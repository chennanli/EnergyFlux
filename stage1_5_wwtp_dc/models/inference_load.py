"""Stage 1.5 Step 7 (partial) — Inference load curve per PRD C.5."""
from __future__ import annotations

import numpy as np
import pandas as pd

P_IT_MAX_KW = 2000
P_DC_TOTAL_KW = 2500  # PUE 1.25
TOKENS_PER_SEC_PER_MW = 5.8e6


def generate_load_factors(hours: int = 8760, seed: int = 42) -> np.ndarray:
    np.random.seed(seed)
    t = np.arange(hours)
    diurnal = 0.50 + 0.45 * np.sin(2 * np.pi * (t - 6) / 24)
    burst = np.random.poisson(lam=0.05, size=hours) * 0.15
    return np.clip(diurnal + burst, 0.20, 1.00)


def generate_dc_load(hours: int = 8760, seed: int = 42) -> pd.DataFrame:
    lf = generate_load_factors(hours, seed)
    return pd.DataFrame(
        {
            "load_factor": lf,
            "P_dc_kw": lf * P_DC_TOTAL_KW,
            "P_it_kw": lf * P_IT_MAX_KW,
        }
    )
