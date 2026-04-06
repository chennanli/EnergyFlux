# Troubleshooting Guide — Solar PV + Grid Anomalies

## Anomaly Category 1: PV Output Below Expected

### Check 1: Weather conditions
- Cloud cover > 50% → reduced irradiance is expected
- Temperature > 40°C → thermal derating (expect 5-12% loss)
- Low wind → higher cell temperature → more derating
- Dust storm / wildfire smoke → severe soiling + irradiance reduction

### Check 2: Equipment status
- Inverter fault code → check inverter display/SCADA
- Tracker stuck → single row producing less, others normal
- String fuse blown → one string offline, ~3% reduction per string
- Communication loss → data gap, not actual generation loss

### Check 3: Gradual degradation
- Month-over-month decline → soiling accumulation
- Year-over-year decline → module degradation (expect 0.5%/year)
- Seasonal pattern → normal (winter has less irradiance)
- Hot spot on thermal image → cell crack or bypass diode failure

## Anomaly Category 2: Grid Voltage Out of Range

### Overvoltage (> 1.05 pu)
- Most common cause: PV generation > local load → reverse power flow
- Time pattern: typically 10am-2pm on clear days
- Severity increases with: higher PV penetration, longer feeder, lower load
- Immediate action: check BESS charging (should absorb surplus)
- If BESS full (SOC=90%): consider PV curtailment or load shifting

### Undervoltage (< 0.95 pu)
- Most common cause: high load + no generation (evening peak, no PV)
- Time pattern: typically 5-9pm, especially winter
- Severity increases with: EV charging peak, cold weather (heating loads)
- Immediate action: check BESS discharge (should supply deficit)
- If BESS empty (SOC=10%): request utility support or load shedding

### Voltage oscillation
- Rapid cycling between high/low → possible inverter hunting
- Check inverter reactive power settings
- Check BESS control stability
- May indicate transformer tap changer cycling

## Anomaly Category 3: Line Overloading

### Causes
- Simultaneous high PV export + high load on adjacent buses
- BESS charging at full rate during PV peak
- EV charging cluster during evening peak

### Actions
- Check line loading percentage (> 80% = warning, > 100% = critical)
- Reduce BESS charge rate if line to BESS is congested
- Stagger EV charging schedules
- Consider line upgrade if persistent

## Anomaly Category 4: BESS Issues

### SOC stuck at minimum (10%)
- BESS not charging → check PV output, check charge controller
- Possible: charge circuit fault, BMS lockout, thermal protection

### SOC stuck at maximum (90%)
- BESS not discharging → check discharge schedule, inverter status
- Result: PV surplus not absorbed → overvoltage risk

### Rapid cycling
- BESS charging and discharging within same hour
- Check control logic for oscillation
- May indicate conflicting setpoints (voltage vs. schedule control)
