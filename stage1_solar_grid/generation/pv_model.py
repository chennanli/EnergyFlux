"""
Sprint 3: PV Generation Modeling — 4-Mode Comparison (corrected)
=================================================================
Four configurations with physically accurate modeling:

  Mode 1: Fixed tilt 20 degrees — FixedMount, standard ModelChain
  Mode 2: 1P SAT, no backtracking — pvfactors row-to-row shading (correct)
  Mode 3: 1P SAT + backtracking — standard ModelChain (backtrack removes shading)
  Mode 4: 1P SAT + backtracking + bifacial — pvfactors bifacial irradiance (correct)

Modes 2 and 4 use solarfactors (pvlib community fork of SunPower/pvfactors)
to correctly calculate row-to-row shading and bifacial rear irradiance.
Install: uv pip install solarfactors

Location : Fremont, CA (37.5485 N, 121.9886 W)
Array    : 10 trackers x 3 strings x 16 modules, Hanwha Q CELLS Q.PEAK DUO L-G5.2 390W
           DC = 187.2 kWp, ILR = 1.2, AC = 156 kW

Input :  stage1_solar_grid/data/raw/weather_fremont.csv
Output:  stage1_solar_grid/data/processed/pv_comparison.csv
         stage1_solar_grid/data/processed/pv_comparison_plot.png
"""

import warnings
warnings.filterwarnings("ignore", module="pvfactors")

import pandas as pd
import numpy as np
import pvlib
from pvlib.location import Location
from pvlib.pvsystem import PVSystem, Array, FixedMount, SingleAxisTrackerMount
from pvlib.modelchain import ModelChain
from pvlib.bifacial.pvfactors import pvfactors_timeseries
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ── Paths ─────────────────────────────────────────────────────────────────────
RAW_PATH      = Path(__file__).parent.parent / "data" / "raw" / "weather_fremont.csv"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# ── Location ──────────────────────────────────────────────────────────────────
LAT      = 37.5485
LON      = -121.9886
ALTITUDE = 23
TIMEZONE = "America/Los_Angeles"

# ── Array config (identical for all 4 modes) ──────────────────────────────────
NUM_TRACKERS        = 10
STRINGS_PER_TRACKER = 3
MODULES_PER_STRING  = 16
MODULE_WP           = 390

TOTAL_STRINGS = NUM_TRACKERS * STRINGS_PER_TRACKER    # 30
TOTAL_MODULES = TOTAL_STRINGS * MODULES_PER_STRING    # 480
DC_KWP        = TOTAL_MODULES * MODULE_WP / 1000      # 187.2 kWp
ILR           = 1.2
AC_KW         = DC_KWP / ILR                          # 132 kW

# ── Physical dimensions of CS6U-330M ─────────────────────────────────────────
PVROW_WIDTH  = 2.015   # module long edge (portrait), meters
PVROW_HEIGHT = 1.5     # center height above ground, meters

# ── Tracker parameters ────────────────────────────────────────────────────────
FIXED_TILT   = 20
AXIS_AZIMUTH = 180
MAX_ANGLE    = 60
GCR          = 0.35

# ── Bifacial parameters (mode 4 only) ─────────────────────────────────────────
BIFACIALITY  = 0.70
ALBEDO       = 0.25


# ── Load weather ──────────────────────────────────────────────────────────────
def load_weather(path):
    df = pd.read_csv(path, index_col="timestamp", parse_dates=True)
    df.index = df.index.tz_localize(
        TIMEZONE, nonexistent="shift_forward", ambiguous="NaT"
    )
    df = df[df.index.notna()]
    weather = pd.DataFrame({
        "ghi"       : df["ghi_wm2"],
        "dni"       : df["dni_wm2"],
        "dhi"       : df["dhi_wm2"],
        "temp_air"  : df["temp_c"],
        "wind_speed": df["wind_ms"],
    })
    print(f"Weather loaded: {len(weather)} rows "
          f"({weather.index[0].date()} to {weather.index[-1].date()})")
    return weather


# ── Find inverter ─────────────────────────────────────────────────────────────
def find_inverter(inverters, target_kw, tolerance_pct=20):
    target_w   = target_kw * 1000
    candidates = inverters.loc["Paco"]
    mask       = (candidates >= target_w * (1 - tolerance_pct/100)) & \
                 (candidates <= target_w * (1 + tolerance_pct/100))
    matches    = candidates[mask].sort_values()
    if matches.empty:
        raise ValueError(f"No inverter found near {target_kw:.0f} kW.")
    return inverters[matches.index[len(matches) // 2]]


# ── MODE 1 & 3: standard ModelChain ──────────────────────────────────────────
def run_modelchain(mode, modules_db, inverters_db, location, weather):
    if mode == 1:
        mount = FixedMount(
            surface_tilt    = FIXED_TILT,
            surface_azimuth = AXIS_AZIMUTH,
        )
    else:  # mode 3
        mount = SingleAxisTrackerMount(
            axis_tilt    = 0,
            axis_azimuth = AXIS_AZIMUTH,
            max_angle    = MAX_ANGLE,
            backtrack    = True,
            gcr          = GCR,
        )

    module   = modules_db["Hanwha_Q_Cells_Q_PEAK_DUO_L_G5_2_390"].copy()
    inverter = find_inverter(inverters_db, AC_KW)

    system = PVSystem(
        arrays=[Array(
            mount                        = mount,
            module_parameters            = module,
            temperature_model_parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS[
                "sapm"]["open_rack_glass_glass"],
            modules_per_string           = MODULES_PER_STRING,
            strings                      = TOTAL_STRINGS,
        )],
        inverter_parameters = inverter,
    )

    mc = ModelChain(system, location, aoi_model="physical", spectral_model="no_loss")
    mc.run_model(weather)
    return (mc.results.ac / 1000).clip(lower=0)


# ── Electrical mismatch from bypass diode activation ─────────────────────────
# When row-to-row shading occurs, shadow falls on a few cells at the module edge.
# Even a small shadow triggers a bypass diode, shorting out 1/3 of the module
# (96-cell module has 3 bypass groups of 32 cells each).
# pvfactors only models irradiance reduction (~0.2%), but the real electrical
# loss is 5-10x larger due to this step-function bypass diode effect.
# Reference: Deline et al. (2020), NREL/CP-5K00-73541
BYPASS_LOSS_FRACTION = 0.33   # one bypass group = 1/3 of module power lost


# ── MODE 2 & 4: pvfactors irradiance → ModelChain DC/AC ──────────────────────
def run_pvfactors(mode, location, weather, modules_db, inverters_db):
    """
    Mode 2: 1P tracker, NO backtracking — pvfactors calculates row-to-row shading
             + electrical mismatch correction for bypass diode activation
    Mode 4: 1P tracker + backtracking + bifacial — pvfactors calculates rear irradiance

    pvfactors handles step ① (irradiance with shading/bifacial),
    then ModelChain handles steps ②→⑤ (DC model, losses, inverter)
    so all 4 modes use the same loss chain.
    """
    solpos = location.get_solarposition(weather.index)

    tracking = pvlib.tracking.singleaxis(
        apparent_zenith  = solpos["apparent_zenith"],
        solar_azimuth    = solpos["azimuth"],
        axis_tilt        = 0,
        axis_azimuth     = AXIS_AZIMUTH,
        max_angle        = MAX_ANGLE,
        backtrack        = (mode == 4),   # False for mode 2, True for mode 4
        gcr              = GCR,
    )
    surface_tilt    = tracking["surface_tilt"].fillna(90)
    surface_azimuth = tracking["surface_azimuth"].fillna(AXIS_AZIMUTH)

    # pvfactors returns 4 values: raw front/rear + AOI-absorbed front/rear
    _, _, irrad_front_abs, irrad_rear_abs = pvfactors_timeseries(
        solar_azimuth        = solpos["azimuth"],
        solar_zenith         = solpos["apparent_zenith"],
        surface_azimuth      = surface_azimuth,
        surface_tilt         = surface_tilt,
        axis_azimuth         = AXIS_AZIMUTH,
        timestamps           = weather.index,
        dni                  = weather["dni"],
        dhi                  = weather["dhi"],
        gcr                  = GCR,
        pvrow_height         = PVROW_HEIGHT,
        pvrow_width          = PVROW_WIDTH,
        albedo               = ALBEDO,
        n_pvrows             = 3,
        index_observed_pvrow = 1,
    )

    # Combine front + rear (bifacial) or front only
    if mode == 4:
        eff_irrad = irrad_front_abs.fillna(0) + BIFACIALITY * irrad_rear_abs.fillna(0)
    else:
        eff_irrad = irrad_front_abs.fillna(0)

    # ── Electrical mismatch correction for Mode 2 (no backtracking) ──────
    # Detect shading hours by comparing tracker angles with vs without backtracking.
    # When angles differ, the tracker is beyond the backtracking limit → row shading.
    # Shadow on module edge triggers bypass diode → lose ~1/3 module power.
    # Shade severity scales with how far past the backtracking angle the tracker is.
    if mode == 2:
        tracking_bt = pvlib.tracking.singleaxis(
            apparent_zenith  = solpos["apparent_zenith"],
            solar_azimuth    = solpos["azimuth"],
            axis_tilt        = 0,
            axis_azimuth     = AXIS_AZIMUTH,
            max_angle        = MAX_ANGLE,
            backtrack        = True,
            gcr              = GCR,
        )
        # Angle excess beyond backtracking limit (degrees)
        angle_excess = (tracking["surface_tilt"].fillna(0)
                        - tracking_bt["surface_tilt"].fillna(0)).abs()
        # Shade severity: 0 = no shade, 1 = deep shade
        # Normalise by max_angle; saturates quickly because bypass diode
        # triggers even with small shadow coverage
        shade_severity = (angle_excess / (MAX_ANGLE * 0.3)).clip(0, 1)
        # Apply bypass diode mismatch penalty
        mismatch_factor = 1 - BYPASS_LOSS_FRACTION * shade_severity
        eff_irrad = eff_irrad * mismatch_factor

    # Cell temperature — same SAPM model as modes 1 & 3
    temp_params = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS[
        "sapm"]["open_rack_glass_glass"]
    temp_cell = pvlib.temperature.sapm_cell(
        poa_global = eff_irrad,
        temp_air   = weather["temp_air"],
        wind_speed = weather["wind_speed"],
        **temp_params,
    )

    # Build same PVSystem as modes 1 & 3 for identical DC/AC loss chain
    mount = SingleAxisTrackerMount(
        axis_tilt    = 0,
        axis_azimuth = AXIS_AZIMUTH,
        max_angle    = MAX_ANGLE,
        backtrack    = (mode == 4),
        gcr          = GCR,
    )
    module   = modules_db["Hanwha_Q_Cells_Q_PEAK_DUO_L_G5_2_390"].copy()
    inverter = find_inverter(inverters_db, AC_KW)

    system = PVSystem(
        arrays=[Array(
            mount                        = mount,
            module_parameters            = module,
            temperature_model_parameters = temp_params,
            modules_per_string           = MODULES_PER_STRING,
            strings                      = TOTAL_STRINGS,
        )],
        inverter_parameters = inverter,
    )

    mc = ModelChain(system, location, aoi_model="physical", spectral_model="no_loss")

    # Feed pvfactors irradiance into ModelChain (skips POA calc, uses same DC/AC chain)
    data = pd.DataFrame({
        "effective_irradiance": eff_irrad,
        "cell_temperature":     temp_cell,
    })
    mc.run_model_from_effective_irradiance(data)
    return (mc.results.ac / 1000).clip(lower=0)


# ── Run all 4 modes ───────────────────────────────────────────────────────────
def run_all_modes(weather):
    location     = Location(LAT, LON, tz=TIMEZONE, altitude=ALTITUDE, name="Fremont CA")
    modules_db   = pvlib.pvsystem.retrieve_sam("CECMod")
    inverters_db = pvlib.pvsystem.retrieve_sam("cecinverter")

    labels = {
        1: "Fixed tilt 20 deg",
        2: "1P tracker (no backtrack)",
        3: "1P tracker + backtrack",
        4: "Bifacial + backtrack",
    }

    results = {}
    for mode in (1, 2, 3, 4):
        print(f"\n── Mode {mode}: {labels[mode]} ──")
        if mode in (1, 3):
            ac_kw = run_modelchain(mode, modules_db, inverters_db, location, weather)
        else:
            ac_kw = run_pvfactors(mode, location, weather, modules_db, inverters_db)

        annual_mwh = ac_kw.sum() / 1000
        cf         = ac_kw.mean() / DC_KWP * 100
        print(f"  Annual energy   : {annual_mwh:.1f} MWh")
        print(f"  Capacity factor : {cf:.1f}%")
        print(f"  Peak AC output  : {ac_kw.max():.1f} kW")
        results[labels[mode]] = ac_kw

    return results


# ── Plot ──────────────────────────────────────────────────────────────────────
def plot_comparison(results):
    colors = ["#888780", "#E24B4A", "#185FA5", "#1D9E75"]
    labels = list(results.keys())

    fig = plt.figure(figsize=(16, 10))
    gs  = gridspec.GridSpec(2, 2, hspace=0.45, wspace=0.35)

    ax1 = fig.add_subplot(gs[0, :])
    for i, (label, ac_kw) in enumerate(results.items()):
        week = ac_kw["2022-06-21":"2022-06-28"]
        ax1.plot(week.index, week, label=label, color=colors[i],
                 linewidth=1.4, alpha=0.9)
    ax1.axhline(AC_KW, color="black", linewidth=0.8, linestyle="--",
                alpha=0.4, label=f"Inverter limit {AC_KW:.0f} kW")
    ax1.set_title("AC Power — Summer week June 21-28 2022", fontsize=11)
    ax1.set_ylabel("AC Power (kW)")
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.2)

    ax2 = fig.add_subplot(gs[1, 0])
    monthly = {l: results[l].resample("ME").sum() / 1000 for l in labels}
    months  = monthly[labels[0]].index.strftime("%b")
    x, w   = range(len(months)), 0.18
    for i, label in enumerate(labels):
        offset = (i - 1.5) * w
        ax2.bar([xi + offset for xi in x], monthly[label].values,
                width=w, label=label, color=colors[i], alpha=0.85)
    ax2.set_xticks(list(x))
    ax2.set_xticklabels(months, fontsize=8)
    ax2.set_title("Monthly Energy (MWh)", fontsize=11)
    ax2.set_ylabel("MWh")
    ax2.legend(fontsize=7)
    ax2.grid(True, alpha=0.2, axis="y")

    ax3 = fig.add_subplot(gs[1, 1])
    annual   = [results[l].sum() / 1000 for l in labels]
    baseline = annual[0]
    bars = ax3.bar(range(4), annual, color=colors, alpha=0.85, width=0.55)
    for i, (bar, val) in enumerate(zip(bars, annual)):
        pct  = (val - baseline) / baseline * 100
        sign = "+" if pct >= 0 else ""
        ax3.text(bar.get_x() + bar.get_width()/2, val + 1,
                 f"{val:.0f} MWh\n({sign}{pct:.1f}%)",
                 ha="center", va="bottom", fontsize=8.5)
    ax3.set_xticks(range(4))
    ax3.set_xticklabels(["Fixed\ntilt", "1P no\nbacktrack",
                          "1P +\nbacktrack", "Bifacial\n+backtrack"], fontsize=8)
    ax3.set_title("Annual Energy vs fixed tilt baseline", fontsize=11)
    ax3.set_ylabel("MWh / year")
    ax3.grid(True, alpha=0.2, axis="y")

    fig.suptitle(
        f"PV Config Comparison — Fremont CA  |  "
        f"DC={DC_KWP:.0f} kWp  |  AC={AC_KW:.0f} kW  |  ILR={ILR}  |  GCR={GCR}",
        fontsize=12
    )

    out = PROCESSED_DIR / "pv_comparison_plot.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"\nPlot saved: {out}")
    plt.show()


# ── Save CSV ──────────────────────────────────────────────────────────────────
def save_csv(results):
    df_out = pd.DataFrame(results)
    out = PROCESSED_DIR / "pv_comparison.csv"
    df_out.to_csv(out)
    print(f"CSV saved: {out}")


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    weather = load_weather(RAW_PATH)
    results = run_all_modes(weather)
    save_csv(results)
    plot_comparison(results)
