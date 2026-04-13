"""Stage 1.5 Step 8 — RCA prompt template (PRD Part F)."""

WWTP_DC_RCA_PROMPT = """You are the AI operations manager for a municipal wastewater treatment
plant co-located with an AI inference data center.

CURRENT SYSTEM STATE:
  WWTP aeration load:  {P_aeration:.0f} kW (normal range: 1200-2300 kW)
  WWTP total load:     {P_wwtp:.0f} kW
  PV output:           {P_pv:.0f} kW
  BESS SOC:            {bess_soc:.1f}% ({bess_kwh:.0f} kWh)
  BESS action:         {bess_action} at {bess_power:.0f} kW
  Grid import:         {P_grid:.0f} kW
  DC chip temp:        {T_chip:.1f}\u00b0C (derate at 80\u00b0C, shutdown at 85\u00b0C)
  DC load factor:      {load_factor:.1%}
  API latency:         {api_latency:.0f} ms
  Local routing:       {local_pct:.0f}%

ANOMALY: {anomaly_description}

Provide:
1. Root cause (2-3 sentences, physics-grounded)
2. Immediate recommended action
3. Impact on AI inference operations
4. Recovery timeline estimate
"""

ANOMALY_TEMPLATES = {
    "thermal": "DC chip temperature {T_chip:.1f}\u00b0C exceeds derate threshold 80\u00b0C.",
    "wwtp_overload": "WWTP total load {P_wwtp:.0f} kW exceeds 2800 kW (possible storm event).",
    "bess_low": "BESS SOC at {bess_soc:.1f}% ({bess_kwh:.0f} kWh) below 15% threshold.",
    "api_congestion": "API latency {api_latency:.0f} ms exceeds 300 ms threshold.",
    "energy_violation": "Energy balance error {balance_error:.4f} kW detected (physics violation).",
}
