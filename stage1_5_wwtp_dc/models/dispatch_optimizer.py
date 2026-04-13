"""Stage 1.5 — Pyomo LP dispatch optimizer (STUB — do not implement yet).

This stub defines the optimization model structure for replacing the
rule-based dispatch state machine (bess_dispatch.py) with a rolling-horizon
LP/MIP that minimizes total electricity cost.

Prerequisites before implementing:
  1. WWTP physics model verified (DO dynamics, Part 8) ✓ DONE
  2. Rule-based dispatch validated against real TOU rates ← in progress
  3. At least 1 month of dispatch results to calibrate demand threshold

References:
  - Handoff document Part 3 (dispatch state machine — the rule-based version)
  - Handoff document Part 5 Priority 4
  - PG&E E-20 rate structure (Part 3.1)
"""
from __future__ import annotations

# TODO: pip install pyomo highspy (HiGHS solver, open-source LP/MIP)

# ─── MODEL STRUCTURE ────────────────────────────────────────────────────────
#
# Sets:
#   T = {0, 1, ..., horizon_hours - 1}   # typically 24h or 48h rolling
#
# Parameters (from simulation data):
#   P_pv[t]         kW    PV generation forecast
#   P_wwtp[t]       kW    WWTP load forecast (from DO dynamics model)
#   P_dc[t]         kW    DC load forecast (from inference_load model)
#   price[t]        $/kWh TOU electricity price at hour t
#   P_biogas        kW    constant biogas generation (800 kW)
#
# Decision Variables:
#   P_chg[t]        kW    BESS charge rate at hour t      (≥ 0)
#   P_dis[t]        kW    BESS discharge rate at hour t   (≥ 0)
#   P_grid[t]       kW    grid import at hour t           (≥ 0, no export)
#   P_curtail[t]    kW    PV curtailment at hour t        (≥ 0)
#   SOC[t]          kWh   state of charge at hour t
#   P_grid_peak     kW    peak 15-min grid draw (for demand charge)
#
# Objective:
#   minimize  Σ_t [ price[t] × P_grid[t] ]          # energy cost
#           + demand_charge_rate × P_grid_peak       # demand charge (~$15/kW/month)
#           - export_revenue (if applicable)
#
# Constraints:
#   Energy balance (every t):
#     P_pv[t] + P_dis[t] + P_grid[t] + P_biogas
#       = P_wwtp[t] + P_dc[t] + P_chg[t] + P_curtail[t]
#
#   SOC dynamics:
#     SOC[t+1] = SOC[t] + P_chg[t] × η_chg - P_dis[t] / η_dis
#
#   SOC bounds:
#     800 ≤ SOC[t] ≤ 7600    (10%–95% of 8,000 kWh)
#
#   Charge/discharge limits (asymmetric):
#     P_chg[t] ≤ 1000         (slow charge — transformer protection)
#     P_dis[t] ≤ 2000         (fast discharge — peak shaving)
#
#   No simultaneous charge + discharge:
#     P_chg[t] × P_dis[t] = 0  (bilinear → use binary variable or SOS1)
#
#   Grid no-export:
#     P_grid[t] ≥ 0
#
#   Demand charge tracking:
#     P_grid_peak ≥ P_grid[t]   ∀ t   (peak tracking)
#
# ─── PLACEHOLDER IMPLEMENTATION ─────────────────────────────────────────────

def create_model():
    """Create Pyomo ConcreteModel for BESS dispatch optimization.

    TODO: Implement after rule-based dispatch is fully validated.
    """
    raise NotImplementedError(
        "Pyomo optimizer is a placeholder. "
        "Use models.bess_dispatch.dispatch_step() for rule-based dispatch. "
        "Implement this after validating rule-based results against real TOU bills."
    )


# ─── NOTES FOR IMPLEMENTATION ───────────────────────────────────────────────
#
# 1. Use HiGHS solver (open-source, fast for LP/MIP):
#      import pyomo.environ as pyo
#      solver = pyo.SolverFactory('appsi_highs')
#
# 2. Rolling horizon: solve 48h ahead, apply first 24h, re-solve with
#    updated weather forecast. This handles forecast uncertainty.
#
# 3. The binary variable for no-simultaneous-charge/discharge adds MIP
#    complexity. For first implementation, use LP relaxation (allow small
#    simultaneous flows, check ex-post that they're negligible).
#
# 4. Demand charge is per billing period (monthly). For daily optimization,
#    track running monthly peak and only penalize if new peak exceeds it.
#
# 5. Validate against rule-based dispatch: Pyomo should produce LOWER cost
#    because it has perfect foresight within the horizon. If it doesn't,
#    the model formulation has a bug.
