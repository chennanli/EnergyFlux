"""
Sprint 3: PV Generation Modeling with PVlib
============================================
Models AC power output of a 10-row Single-Axis Tracker (1P) array (~250 kW).
This matches real-world utility-scale deployments (e.g. NEXTracker NX Horizon).

Tracker type: Single-Axis Tracker (SAT), 1P configuration
  - Axis runs North-South
  - Panels rotate East-West following the sun throughout the day
  - Max rotation angle +/-60 degrees (standard for most sites)
  - ~20-25% more energy than fixed-tilt at this latitude

Location: Fremont, CA (37.5485 N, 121.9886 W)
Array   : 10 rows x 1P, Canadian Solar CS6U-330M, 250 modules total
Inverter: SMA Sunny Tripower

Input:  stage1_solar_grid/data/raw/weather_fremont.csv
Output: stage1_solar_grid/data/processed/pv_generation.csv
"""

import pandas as pd
import pvlib
from pvlib.location import Location
from pvlib.pvsystem import PVSystem, Array, SingleAxisTrackerMount
from pvlib.modelchain import ModelChain
from pathlib import Path
import matplotlib.pyplot as plt

# ── Paths ─────────────────────────────────────────────────────────────────────
RAW_PATH      = Path(__file__).parent.parent / "data" / "raw" / "weather_fremont.csv"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# ── Location ──────────────────────────────────────────────────────────────────
LAT      = 37.5485
LON      = -121.9886
ALTITUDE = 23
TIMEZONE = "America/Los_Angeles"

# ── Tracker parameters ────────────────────────────────────────────────────────
AXIS_TILT    = 0
AXIS_AZIMUTH = 180
MAX_ANGLE    = 60


# ── Load weather data ─────────────────────────────────────────────────────────
def load_weather(path):
    df = pd.read_csv(path, index_col="timestamp", parse_dates=True)

    df.index = df.index.tz_localize(
        TIMEZONE,
        nonexistent="shift_forward",
        ambiguous="NaT"
    )
    df = df[df.index.notna()]

    weather = pd.DataFrame({
        "ghi"       : df["ghi_wm2"],
        "dni"       : df["dni_wm2"],
        "dhi"       : df["dhi_wm2"],
        "temp_air"  : df["temp_c"],
        "wind_speed": df["wind_ms"],
    })

    print(f"Weather loaded: {len(weather)} rows")
    print(f"Range: {weather.index[0]} -> {weather.index[-1]}")
    return weather


# ── Build PV system with Single-Axis Tracker ──────────────────────────────────
def build_system():
    location = Location(
        latitude  = LAT,
        longitude = LON,
        tz        = TIMEZONE,
        altitude  = ALTITUDE,
        name      = "Fremont CA"
    )

    modules   = pvlib.pvsystem.retrieve_sam("CECMod")
    inverters = pvlib.pvsystem.retrieve_sam("cecinverter")

    module   = modules["Canadian_Solar_Inc__CS6U_330M"]
    inverter = inverters["SMA_America__STP20000TL_US_10__480V_"]

    tracker_mount = SingleAxisTrackerMount(
        axis_tilt    = AXIS_TILT,
        axis_azimuth = AXIS_AZIMUTH,
        max_angle    = MAX_ANGLE,
        backtrack    = True,
        gcr          = 0.35,
    )

    system = PVSystem(
        arrays=[
            Array(
                mount                        = tracker_mount,
                module_parameters            = module,
                temperature_model_parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS[
                    "sapm"]["open_rack_glass_glass"],
                modules_per_string           = 25,
                strings                      = 10,
            )
        ],
        inverter_parameters = inverter,
    )

    dc_capacity = 10 * 25 * 330 / 1000
    print(f"\nSystem configuration:")
    print(f"  Type    : Single-Axis Tracker (1P), backtracking enabled")
    print(f"  Module  : Canadian Solar CS6U-330M (330 Wp)")
    print(f"  Array   : 10 strings x 25 modules = 250 modules")
    print(f"  DC cap  : {dc_capacity:.1f} kWp")
    print(f"  Tracker : axis N-S, max +/-{MAX_ANGLE} deg, GCR=0.35")

    return location, system


# ── Run simulation ────────────────────────────────────────────────────────────
def run_simulation(location, system, weather):
    mc = ModelChain(system, location, aoi_model="physical", spectral_model="no_loss")

    print("\nRunning simulation...")
    mc.run_model(weather)

    ac_kw = mc.results.ac / 1000
    ac_kw = ac_kw.clip(lower=0)

    print(f"\nResults:")
    print(f"  Peak AC output  : {ac_kw.max():.1f} kW")
    print(f"  Annual energy   : {ac_kw.sum() / 1000:.1f} MWh  (over data period)")
    print(f"  Capacity factor : {ac_kw.mean() / (10 * 25 * 330 / 1000) * 100:.1f}%")

    return ac_kw


# ── Save and plot ─────────────────────────────────────────────────────────────
def save_and_plot(weather, ac_kw):
    output = pd.DataFrame({
        "ac_power_kw" : ac_kw,
        "ghi_wm2"     : weather["ghi"],
        "temp_c"      : weather["temp_air"],
    })
    out_path = PROCESSED_DIR / "pv_generation.csv"
    output.to_csv(out_path)
    print(f"\nSaved: {out_path}")

    week = output["2022-06-21":"2022-06-28"]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 7), sharex=True)

    ax1.plot(week.index, week["ghi_wm2"], color="#EF9F27", linewidth=1.2)
    ax1.set_ylabel("GHI (W/m2)")
    ax1.set_title("Single-Axis Tracker PV Array — Fremont CA (June 2022)\n"
                  "10 rows x 25 modules, 250 kWp, backtracking enabled")
    ax1.grid(True, alpha=0.3)

    ax2.fill_between(week.index, week["ac_power_kw"], alpha=0.5, color="#185FA5")
    ax2.plot(week.index, week["ac_power_kw"], color="#185FA5", linewidth=1.2)
    ax2.set_ylabel("AC Power (kW)")
    ax2.set_xlabel("Time")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plot_path = PROCESSED_DIR / "pv_generation_plot.png"
    plt.savefig(plot_path, dpi=150)
    print(f"Plot: {plot_path}")
    plt.show()


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    weather          = load_weather(RAW_PATH)
    location, system = build_system()
    ac_kw            = run_simulation(location, system, weather)
    save_and_plot(weather, ac_kw)
