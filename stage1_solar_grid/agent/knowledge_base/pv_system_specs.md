# PV System Specifications — Fremont CA Industrial Park

## Array Configuration
- Module: Hanwha Q CELLS Q.PEAK DUO L-G5.2 390W (mono-Si, 144 half-cells)
- Array: 10 trackers × 3 strings × 16 modules = 480 modules total
- DC capacity: 187.2 kWp
- AC capacity: 156 kW (ILR = 1.2)
- Tracker: Single-axis (N-S axis), ±60° max angle, GCR = 0.35
- Backtracking: enabled (avoids row-to-row shading at low sun angles)

## Module Parameters
- STC power: 390 W
- Temperature coefficient (gamma): -0.354 %/°C
- NOCT: 46.4°C
- Cell area: 1.95 m²
- Technology: Mono-crystalline Si

## Location
- Fremont, CA (37.5485°N, 121.9886°W)
- Altitude: 23 m
- Timezone: America/Los_Angeles
- Typical annual GHI: ~1,800 kWh/m²

## Expected Performance
- Annual energy (Mode 3, backtracking): ~773 MWh
- Capacity factor: ~23.6%
- Peak AC output: 135 kW

## Common Degradation Factors
- Soiling (dust/dirt): 2-5% loss if not cleaned
- Module degradation: 0.5%/year typical for mono-Si
- Inverter clipping: occurs when DC > AC capacity (ILR=1.2 → ~5-8% clipping)
- Temperature derating: 5-8% loss in summer (Fremont peak ~40°C ambient)
- Wiring/mismatch: ~1-2% system loss

## Anomaly Indicators
- Output < 80% of clear-sky expectation → check weather (clouds) first
- Output < 50% of expectation on clear day → possible equipment failure
- Gradual decline over weeks → soiling or degradation
- Sudden drop to zero → inverter trip, breaker open, or communication loss
