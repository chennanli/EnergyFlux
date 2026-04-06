# Grid Specifications — Commercial Block Distribution Network (Fremont CA)

## Network Topology
- Voltage level: 0.4 kV (LV distribution)
- Transformer: 400 kVA, 10kV/0.4kV
- 9 buses, 7 lines (NAYY 4x120 SE LV cable)
- Radial topology (star from LV busbar)

## Bus List
| Bus | Name | Type | Rated Power |
|-----|------|------|-------------|
| 0 | MV Grid | External grid (slack) | Infinite |
| 1 | LV Busbar | Distribution | - |
| 2 | PV Plant | Generation | 187 kWp |
| 3 | BESS | Storage | 100 kW / 400 kWh |
| 4 | Biotech Lab | Load | 70 kW (24/7 base + daytime staff) |
| 5 | Supermarket | Load | 45-65 kW (refrigeration 24/7) |
| 6 | EV Charging Hub | Load | 5-60 kW (evening commuter peak) |
| 7 | Medical Clinic | Load | 30 kW (weekday daytime only) |
| 8 | Office Building | Load | 25 kW (weekday daytime only) |

## Voltage Limits (ANSI C84.1 Range A)
- Minimum: 0.95 pu (380 V)
- Maximum: 1.05 pu (420 V)
- Emergency limit: 1.10 pu (440 V — inverter curtailment threshold)

## Overvoltage Analysis
- 4,688 hours per year above 1.05 pu at PV bus
- Maximum voltage: 1.068 pu at PV Plant bus
- Root cause: PV generation exceeds local load during midday → reverse power flow → voltage rise
- Worst months: May-August (highest solar irradiance)
- Worst hours: 10am-2pm (peak PV output, low industrial load)

## Line Loading
- Maximum: 75.8% on Line PV (2km cable from busbar to PV plant)
- No lines exceed 80% thermal limit
- PV line is the bottleneck — longer cable + high PV injection

## BESS Configuration
- Power: 100 kW (charge/discharge)
- Energy: 400 kWh (usable)
- Round-trip efficiency: 95%
- SOC range: 10% - 90%
- Strategy: charge during PV peak (absorb surplus), discharge during evening peak
- Annual cycles: ~400

## Mitigation Strategies for Overvoltage
1. Increase BESS capacity to absorb more PV surplus
2. Reactive power compensation (inverter VAR support)
3. Transformer tap adjustment
4. Curtail PV output above voltage threshold (last resort)
5. Add local loads to consume PV power (e.g., EV charging during daytime)
