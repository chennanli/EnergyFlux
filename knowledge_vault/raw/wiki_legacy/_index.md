# design_wiki — index

Curated design knowledge for behind-the-meter AI factory sites. Follows
Karpathy's LLM Wiki pattern: one concept per file, prose over bullets, every
claim backed by a primary source at the bottom. Re-indexed into FAISS by
`design/rag.py` so the Blog 2 demo can retrieve and cite at query time.

## Hardware
* [hardware/blackwell_gb200_nvl72.md](hardware/blackwell_gb200_nvl72.md) — shipping today, 125 kW/rack, 5.8e6 tok/s per MW
* [hardware/vera_rubin_nvl144.md](hardware/vera_rubin_nvl144.md) — 2026 H2 ship, estimates ±30%, ~3× per-rack inference claim
* [hardware/amd_mi300x.md](hardware/amd_mi300x.md) — MI300X + MI325X alternative path
* [hardware/cerebras_wse3.md](hardware/cerebras_wse3.md) — wafer-scale, niche but shipping

## Photovoltaic technology
* [pv/fixed_tilt.md](pv/fixed_tilt.md) — simplest, lowest CAPEX, −15% yield vs 1-axis
* [pv/single_axis_tracker.md](pv/single_axis_tracker.md) — utility-scale default, +18% over fixed
* [pv/bifacial_gain.md](pv/bifacial_gain.md) — +7% on top of 1-axis, albedo-dependent
* [pv/dual_axis.md](pv/dual_axis.md) — +5% over 1-axis bifacial, +25% CAPEX — rarely justified

## Battery energy storage
* [bess/4h_battery_standard.md](bess/4h_battery_standard.md) — the industry default, covers TOU peak
* [bess/tou_arbitrage.md](bess/tou_arbitrage.md) — economics of night-charge, evening-discharge

## Regulations (state / federal)
* [regulations/tx_ercot_interconnect.md](regulations/tx_ercot_interconnect.md) — TX BTM rules, ERCOT 5 MW threshold
* [regulations/wwtp_buffer_setback.md](regulations/wwtp_buffer_setback.md) — WWTP buffer zones, EPA + state

## CAPEX benchmarks
* [capex/pv_lazard_lcoe_2024.md](capex/pv_lazard_lcoe_2024.md) — $0.85–1.10/W DC, ground-mount utility
* [capex/bess_nrel_atb_2024.md](capex/bess_nrel_atb_2024.md) — $230–320/kWh installed 4-h Li-ion
* [capex/dc_industry_benchmarks.md](capex/dc_industry_benchmarks.md) — $10–15M/MW IT, liquid-cooled
