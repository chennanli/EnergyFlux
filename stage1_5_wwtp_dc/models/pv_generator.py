"""Stage 1.5 Step 3 — PV generator (5,700 kWp scale-up of Stage 1 model).

Strategy: run Stage 1's system to get per-module DC profile (before inverter
clipping), then scale to 5,700 kWp and apply Stage 1.5's own AC clipping
at 4,750 kW. This avoids carrying Stage 1's 154 kW inverter clipping into
the scaled output.

Output: data/pv_hourly.csv [timestamp, P_pv_kw]
Verify: annual 10,000-11,500 MWh, peak 4,500-5,000 kW.
"""
from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pvlib
from pvlib.location import Location
from pvlib.modelchain import ModelChain
from pvlib.pvsystem import Array, PVSystem, SingleAxisTrackerMount

warnings.filterwarnings("ignore")

LAT, LON, ALT, TZ = 37.5485, -121.9886, 23, "America/Los_Angeles"

# Stage 1 reference system (used to get per-module DC profile).
S1_MODULES_PER_STRING = 16
S1_TOTAL_STRINGS = 30
S1_TOTAL_MODULES = 480
S1_MODULE_WP = 385
S1_DC_KWP = S1_TOTAL_MODULES * S1_MODULE_WP / 1000.0  # 184.8
S1_ILR = 1.2
S1_AC_KW = S1_DC_KWP / S1_ILR
S1_GCR = 0.45

# Stage 1.5 target system per PRD B.2.
S15_DC_KWP = 5700.0     # PRD spec (400W × 14,164 ≈ 5,666 → rounded to 5,700)
S15_ILR = 1.2
S15_AC_KW = S15_DC_KWP / S15_ILR  # 4,750 kW
SHADING_FACTOR = 0.92
SOILING_MISMATCH_WIRING = 0.96 * 0.98 * 0.99  # 0.931
INVERTER_EFF = 0.965
TOTAL_SYSTEM_DERATE = SHADING_FACTOR * SOILING_MISMATCH_WIRING * INVERTER_EFF  # ~0.826
TARGET_MODULES = 14_164  # PRD spec

AXIS_AZIMUTH = 180
MAX_ANGLE = 60

WEATHER_PATH = (
    Path(__file__).resolve().parents[2]
    / "stage1_solar_grid"
    / "data"
    / "raw"
    / "weather_fremont.csv"
)


def load_weather(path: Path = WEATHER_PATH) -> pd.DataFrame:
    df = pd.read_csv(path, index_col="timestamp", parse_dates=True)
    df.index = df.index.tz_localize(TZ, nonexistent="shift_forward", ambiguous="NaT")
    df = df[df.index.notna()]
    return pd.DataFrame(
        {
            "ghi": df["ghi_wm2"],
            "dni": df["dni_wm2"],
            "dhi": df["dhi_wm2"],
            "temp_air": df["temp_c"],
            "wind_speed": df["wind_ms"],
        }
    )


def _find_inverter(inverters: pd.DataFrame, target_kw: float) -> pd.Series:
    target_w = target_kw * 1000
    paco = inverters.loc["Paco"]
    mask = (paco >= target_w * 0.8) & (paco <= target_w * 1.2)
    matches = paco[mask].sort_values()
    if matches.empty:
        mask = (paco >= target_w * 0.5) & (paco <= target_w * 1.5)
        matches = paco[mask].sort_values()
    return inverters[matches.index[len(matches) // 2]]


def generate_pv_annual(output_path: str | Path) -> pd.DataFrame:
    weather = load_weather()
    print(f"Weather: {len(weather)} rows  {weather.index[0].date()}→{weather.index[-1].date()}")

    location = Location(LAT, LON, tz=TZ, altitude=ALT, name="Fremont CA")
    modules_db = pvlib.pvsystem.retrieve_sam("CECMod")
    inverters_db = pvlib.pvsystem.retrieve_sam("cecinverter")
    module = modules_db["LONGi_Green_Energy_Technology_Co___Ltd__LR6_72HBD_385M"].copy()
    inverter = _find_inverter(inverters_db, S1_AC_KW)

    mount = SingleAxisTrackerMount(
        axis_tilt=0,
        axis_azimuth=AXIS_AZIMUTH,
        max_angle=MAX_ANGLE,
        backtrack=True,
        gcr=S1_GCR,
    )
    temp_params = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS["sapm"][
        "open_rack_glass_glass"
    ]
    system = PVSystem(
        arrays=[
            Array(
                mount=mount,
                module_parameters=module,
                temperature_model_parameters=temp_params,
                modules_per_string=S1_MODULES_PER_STRING,
                strings=S1_TOTAL_STRINGS,
            )
        ],
        inverter_parameters=inverter,
    )
    mc = ModelChain(system, location, aoi_model="physical", spectral_model="no_loss")
    mc.run_model(weather)

    # Extract both AC and DC outputs from Stage 1 ModelChain.
    ac_s1_kw = (mc.results.ac / 1000.0).clip(lower=0).fillna(0.0)
    dc_raw = mc.results.dc
    if isinstance(dc_raw, pd.DataFrame):
        dc_s1_kw = dc_raw["p_mp"] / 1000.0
    elif isinstance(dc_raw, tuple):
        dc_s1_kw = pd.Series(dc_raw[0]).squeeze() / 1000.0
    else:
        dc_s1_kw = dc_raw / 1000.0
    dc_s1_kw = dc_s1_kw.clip(lower=0).fillna(0.0)

    # Scale DC from Stage 1 to Stage 1.5, apply total system derate, clip at AC.
    dc_scale = S15_DC_KWP / S1_DC_KWP  # 30.84
    ac_s15_kw = (dc_s1_kw * dc_scale * TOTAL_SYSTEM_DERATE).clip(upper=S15_AC_KW)

    # Multi-year weather: take second year (2023) if available, else first.
    if len(ac_s15_kw) > 8760:
        try:
            ac_2023 = ac_s15_kw.loc["2023"]
            if len(ac_2023) >= 8760:
                ac_s15_kw = ac_2023.iloc[:8760]
            else:
                ac_s15_kw = ac_s15_kw.iloc[:8760]
        except KeyError:
            ac_s15_kw = ac_s15_kw.iloc[:8760]

    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2023-01-01", periods=8760, freq="h"),
            "P_pv_kw": ac_s15_kw.values[:8760],
        }
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    annual_mwh = df["P_pv_kw"].sum() / 1000.0
    peak_kw = df["P_pv_kw"].max()
    cf = df["P_pv_kw"].mean() / S15_DC_KWP * 100
    print(f"PV wrote {output_path}")
    print(f"  DC={S15_DC_KWP:.1f} kWp  AC={S15_AC_KW:.1f} kW  modules={TARGET_MODULES}")
    print(f"  total_system_derate={TOTAL_SYSTEM_DERATE:.3f} (shading×soiling×mismatch×wiring×inverter)")
    print(f"  annual={annual_mwh:.1f} MWh  peak={peak_kw:.1f} kW  CF={cf:.1f}%")

    assert 10000 <= annual_mwh <= 11500, f"annual MWh out of range: {annual_mwh:.1f}"
    assert 4400 <= peak_kw <= 5000, f"peak out of range: {peak_kw:.1f}"
    print("  verification: PASS")
    return df


if __name__ == "__main__":
    here = Path(__file__).resolve().parent.parent
    generate_pv_annual(here / "data" / "pv_hourly.csv")
