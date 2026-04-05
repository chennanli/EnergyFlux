"""
GCR Sensitivity Analysis — Mode 2 vs Mode 3 shading impact
Shows how row-to-row shading penalty grows with denser arrays.
"""
import warnings
warnings.filterwarnings("ignore", module="pvfactors")

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
import numpy as np
import pvlib
from pvlib.location import Location
from pvlib.pvsystem import PVSystem, Array, SingleAxisTrackerMount
from pvlib.modelchain import ModelChain
from pvlib.bifacial.pvfactors import pvfactors_timeseries

from stage1_solar_grid.generation.pv_model import (
    load_weather, find_inverter, RAW_PATH,
    LAT, LON, ALTITUDE, TIMEZONE,
    AXIS_AZIMUTH, MAX_ANGLE, PVROW_HEIGHT, PVROW_WIDTH, ALBEDO,
    MODULES_PER_STRING, TOTAL_STRINGS, AC_KW, BIFACIALITY,
)

def run_mode_2_3(gcr, location, weather, modules_db, inverters_db):
    """Run Mode 2 (no backtrack) and Mode 3 (backtrack) at a given GCR."""
    solpos = location.get_solarposition(weather.index)
    temp_params = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS["sapm"]["open_rack_glass_glass"]
    module   = modules_db["Canadian_Solar_Inc__CS6U_330M"].copy()
    inverter = find_inverter(inverters_db, AC_KW)

    results = {}
    for mode, backtrack in [(2, False), (3, True)]:
        tracking = pvlib.tracking.singleaxis(
            apparent_zenith=solpos["apparent_zenith"],
            solar_azimuth=solpos["azimuth"],
            axis_tilt=0, axis_azimuth=AXIS_AZIMUTH,
            max_angle=MAX_ANGLE, backtrack=backtrack, gcr=gcr,
        )
        surface_tilt    = tracking["surface_tilt"].fillna(90)
        surface_azimuth = tracking["surface_azimuth"].fillna(AXIS_AZIMUTH)

        _, _, irrad_front_abs, _ = pvfactors_timeseries(
            solar_azimuth=solpos["azimuth"],
            solar_zenith=solpos["apparent_zenith"],
            surface_azimuth=surface_azimuth,
            surface_tilt=surface_tilt,
            axis_azimuth=AXIS_AZIMUTH,
            timestamps=weather.index,
            dni=weather["dni"], dhi=weather["dhi"],
            gcr=gcr, pvrow_height=PVROW_HEIGHT,
            pvrow_width=PVROW_WIDTH, albedo=ALBEDO,
            n_pvrows=3, index_observed_pvrow=1,
        )
        eff_irrad = irrad_front_abs.fillna(0)
        temp_cell = pvlib.temperature.sapm_cell(
            poa_global=eff_irrad, temp_air=weather["temp_air"],
            wind_speed=weather["wind_speed"], **temp_params,
        )

        mount = SingleAxisTrackerMount(
            axis_tilt=0, axis_azimuth=AXIS_AZIMUTH,
            max_angle=MAX_ANGLE, backtrack=backtrack, gcr=gcr,
        )
        system = PVSystem(
            arrays=[Array(
                mount=mount, module_parameters=module,
                temperature_model_parameters=temp_params,
                modules_per_string=MODULES_PER_STRING, strings=TOTAL_STRINGS,
            )],
            inverter_parameters=inverter,
        )
        mc = ModelChain(system, location, aoi_model="physical", spectral_model="no_loss")
        data = pd.DataFrame({"effective_irradiance": eff_irrad, "cell_temperature": temp_cell})
        mc.run_model_from_effective_irradiance(data)
        ac_mwh = (mc.results.ac / 1000).clip(lower=0).sum() / 1000
        results[mode] = ac_mwh

    return results


if __name__ == "__main__":
    weather  = load_weather(RAW_PATH)
    location = Location(LAT, LON, tz=TIMEZONE, altitude=ALTITUDE, name="Fremont CA")
    modules_db   = pvlib.pvsystem.retrieve_sam("CECMod")
    inverters_db = pvlib.pvsystem.retrieve_sam("cecinverter")

    print(f"\n{'GCR':>6} │ {'Mode 2 (no BT)':>15} │ {'Mode 3 (BT)':>12} │ {'Shading Loss':>13} │ {'Row Pitch':>10}")
    print("───────┼─────────────────┼──────────────┼───────────────┼───────────")

    for gcr in [0.30, 0.35, 0.40, 0.45, 0.50, 0.55]:
        pitch = PVROW_WIDTH / gcr
        res = run_mode_2_3(gcr, location, weather, modules_db, inverters_db)
        loss_pct = (res[2] - res[3]) / res[3] * 100
        print(f"{gcr:>6.2f} │ {res[2]:>12.1f} MWh │ {res[3]:>9.1f} MWh │ {loss_pct:>+11.1f}% │ {pitch:>7.1f} m")

    print("\n(Negative = Mode 2 produces LESS than Mode 3 = shading penalty)")
