# Architecture — Stage 1.5 WWTP AI Compute Node

See the ASCII diagram and NVIDIA stack mapping in README.md.

## System overview

Five physical subsystems modeled in the simulation:

1. Solar PV (5,700 kWp, bifacial 1P tracker) — pvlib ModelChain
2. WWTP electrical load (1,800–3,200 kW, BSM1-shaped diurnal) — parametric model
3. BESS (8 MWh, asymmetric 1/2 MW) — TOU-aware state machine
4. AI data center (2 MW IT, 16 racks) — 3-node RC ODE thermal model
5. 10 kV AC internal bus — pandapower 5-bus power flow (standalone verification)

## BTM topology

All assets share a single 10 kV AC internal bus behind the utility meter.
PV has its own AC inverter. BESS has a bidirectional inverter.
No DC coupling — this is AC-coupled architecture.
Grid export is always zero (P_grid >= 0 constraint enforced every hour).

## LLM agent

Rule-based anomaly detection triggers NVIDIA NIM (Llama 3.1 8B Instruct)
for root cause analysis. Falls back to mock mode if NVIDIA_API_KEY not set.
Routing decision (local GPU vs cloud API) based on API latency threshold.

## Data flow

  pv_generator.py        → data/pv_hourly.csv
  wwtp_load_generator.py → data/wwtp_load_hourly.csv
  bess_dispatch.py       → data/dispatch_hourly.csv
  power_flow.py          → data/powerflow_hourly.csv  (standalone)
  run_demo.py --case all → data/case{1,2,3}_results.csv
  streamlit run app.py   → dashboard at localhost:8501
