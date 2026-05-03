# TOU arbitrage — the BESS revenue mechanic

**"Buy low, sell high" applied to electricity.** Utility time-of-use (TOU) rates differ by 3–5× between off-peak (midnight–6 AM) and on-peak (4 PM–9 PM). A BESS that charges cheap and discharges expensive captures that spread minus losses.

## Example: PG&E E-20 (large commercial, CA, 2024)

* Summer on-peak (4 PM–9 PM): **$0.35–0.42 / kWh**.
* Summer super-off-peak (midnight–6 AM): **$0.09–0.12 / kWh**.
* Spread: **$0.23–0.30 / kWh gross**.
* After round-trip efficiency (~92%) and degradation (~$0.02/kWh equivalent): **$0.19–0.26 / kWh net arbitrage value**.

## For a 2-MW DC colocated site

* BESS: 2 MW / 8 MWh (4-hour).
* Full daily cycle: charge 8 MWh off-peak × $0.10 = $800 cost; discharge 7.4 MWh on-peak × $0.38 = $2,810 revenue. Daily net: **~$2,000**.
* 365 days × ~70% utilization of full cycles = **~$510k/yr arbitrage value**.
* That's on top of the DC's token revenue and the PV offset. It's the BESS paying its own capex back over ~8 years at BESS CAPEX $2.5M (8 MWh × $310/kWh).

## Why this is not the whole story

Utility demand charges (on peak kW, not kWh) can be larger than TOU arbitrage. A BESS that shaves peak kW is worth 2–3× what it's worth just on TOU. For this blog we model both separately.

## Sources

* PG&E E-20 rate schedule, effective 2024-03-01.
* NREL "Behind-the-Meter Battery Storage Economics", 2023.
* Wood Mackenzie US Energy Storage Monitor Q4 2024.
