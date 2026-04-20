# Single-axis tracking

**Default choice for utility-scale ground-mount in the US.**

Single-axis horizontal trackers rotate modules east-to-west on one axis to follow the sun. The DC nameplate is the same per module, but the annual yield is **roughly 15–20% higher than fixed tilt** because the modules intercept the sun at higher cosine angles across more of the day.

## Key numbers

* Land density: **~325 kWp DC per acre** at GCR 0.35.
* Specific yield (AC, after derate): **+18% over fixed tilt**, zone-dependent. At 30°N ≈ 1,830 kWh/kWp/yr; at 40°N ≈ 1,600 kWh/kWp/yr.
* CAPEX uplift: **+$0.05 to $0.10/W DC** vs fixed tilt — about 6–10% premium on total project cost.
* Reliability: modern trackers ship with >99% uptime over 20 years; gear backlash is the main failure mode. Design life 25 years.

## When it wins

* Nearly always, for sites >1 MW in the 25°–45°N band. Single-axis beats fixed-tilt on LCOE in almost every modern US ground-mount analysis.

## When it loses

* Site topography rules out tracker rows (slopes >15%, heavy tree shading, narrow irregular parcels).
* Sites north of 50°N where the sun arc is low enough that tracker gain diminishes.

## Interaction with bifacial

Combining single-axis tracking with bifacial modules is the current industry default. See [bifacial_gain.md](bifacial_gain.md) — the gains stack roughly additively: +18% (tracking) +7% (bifacial) ≈ +25% over fixed-tilt mono.

## Sources

* NREL Annual Technology Baseline 2024 (PV chapter).
* Lazard's Levelized Cost of Energy+ 2024, utility-scale ground-mount section.
* Array Technologies and NEXTracker datasheets, 2024.
