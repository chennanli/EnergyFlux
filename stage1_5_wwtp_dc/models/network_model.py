"""Stage 1.5 Step 7 — Network congestion model (PRD C.6).

Three scenarios with LogNormal congestion factors calibrated to PRD targets:
  NORMAL:   mean ~50ms API
  STRESSED: mean ~150ms API
  SEVERE:   mean ~500ms API, 5% packet loss
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# LogNormal μ values calibrated so that 50 × E[LN(μ,σ)] hits PRD targets.
# E[LN(μ,σ)] = exp(μ + σ²/2).  Solve: μ = ln(target/50) - σ²/2.
SCENARIOS = {
    "normal": {"mu": 0.0, "sigma": 0.3, "packet_loss": 0.0},       # mean≈52ms
    "stressed": {"mu": 0.854, "sigma": 0.7, "packet_loss": 0.02},   # mean≈150ms
    "severe": {"mu": 1.583, "sigma": 1.2, "packet_loss": 0.05},     # mean≈500ms
}
LOCAL_LATENCY_MS = 10.0
TOKENS_PER_MW = 5.8e6
P_IT_MAX_MW = 2.0


def generate_network_scenario(
    scenario: str = "normal",
    hours: int = 24,
    seed: int = 42,
    steps_per_hour: int = 12,
) -> pd.DataFrame:
    np.random.seed(seed)
    cfg = SCENARIOS[scenario]
    n = hours * steps_per_hour

    congestion = np.random.lognormal(mean=cfg["mu"], sigma=cfg["sigma"], size=n)
    api_latency = 50.0 * congestion
    packet_loss = np.where(
        np.random.rand(n) < cfg["packet_loss"], 1.0, 0.0
    )

    # Routing decision per PRD C.6.
    local_pct = np.where(api_latency > 200, 1.0, np.where(api_latency > 100, 0.9, 0.7))
    local_pct = np.where(api_latency <= 50, 0.5, local_pct)

    tokens_local = local_pct * P_IT_MAX_MW * TOKENS_PER_MW
    tokens_api = (1 - local_pct) * P_IT_MAX_MW * TOKENS_PER_MW * (1 - packet_loss)

    timestamps = pd.date_range("2023-04-15", periods=n, freq=f"{60 // steps_per_hour}min")
    return pd.DataFrame(
        {
            "timestamp": timestamps,
            "api_latency_ms": api_latency,
            "congestion_factor": congestion,
            "local_pct": local_pct,
            "packet_loss": packet_loss,
            "tokens_local_per_sec": tokens_local,
            "tokens_api_per_sec": tokens_api,
        }
    )


def verify_network() -> None:
    for name in SCENARIOS:
        df = generate_network_scenario(name)
        mean_lat = df["api_latency_ms"].mean()
        max_lat = df["api_latency_ms"].max()
        pct_300 = (df["api_latency_ms"] > 300).mean() * 100
        print(f"  {name:10s}: mean={mean_lat:.0f}ms  max={max_lat:.0f}ms  "
              f">300ms={pct_300:.0f}%  local={df['local_pct'].mean():.0%}")

    # PRD requirements.
    df_severe = generate_network_scenario("severe")
    mean_sev = df_severe["api_latency_ms"].mean()
    assert 300 <= mean_sev <= 800, f"severe mean {mean_sev:.0f}ms not in [300,800]"
    assert (df_severe["api_latency_ms"] > 300).any(), "severe must have spikes >300ms"
    print("  verification: PASS")


if __name__ == "__main__":
    print("Step 7 network verification:")
    verify_network()
