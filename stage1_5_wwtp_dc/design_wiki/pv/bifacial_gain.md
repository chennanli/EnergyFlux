# Bifacial modules — yield gain

**What it is:** a module construction where both the front and back of the cell are photoactive. The back captures diffuse and ground-reflected light that a mono-facial module would waste.

## Key numbers

* Bifacial gain (extra yield over mono-facial at equal DC nameplate): **+5% to +12%** in real deployments.
* Sweet-spot: **single-axis tracker + GCR 0.35** yields ~+7% on average across US latitudes.
* CAPEX uplift vs mono-facial: **+$0.04 to $0.08/W DC** depending on module brand.
* Bifaciality coefficient (ratio of back-side to front-side efficiency): modern TOPCon/HJT modules run 70–80%.

## What drives the gain

The big variable is **albedo** — the reflectance of the ground behind the array. Typical values:

* Dry soil / mown grass: 0.15–0.20 → low bifacial gain (~3–5%).
* White gravel / light concrete: 0.30–0.40 → medium (~7–9%).
* Snow: 0.70–0.90 → extreme (>15%), but only when the ground is snow-covered.

Grass-covered WWTP buffer zones typically give 5–8% gain — the default we use in `pv_tools.py`.

## Interaction with tracking

Bifacial on fixed-tilt: ~+3–5% (narrower aperture).
Bifacial on single-axis: ~+6–8% (the combo is the industry workhorse).
Bifacial on dual-axis: diminishing returns — the dual-axis geometry already captures most of what bifacial offers.

## Sources

* NREL Technical Report TP-5K00-67198 "Bifacial PV Performance".
* SolarEdge, Longi, Jinko bifacial product datasheets.
* PV Magazine bifacial tracker studies 2022–2024.
