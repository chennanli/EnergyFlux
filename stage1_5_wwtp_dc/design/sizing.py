"""Pure sizing function. Takes an archetype name, returns a complete report.

The report shape is stable across archetypes so callers (Streamlit UI,
future Gemma orchestrator tool) can format it uniformly.

Usage
-----
>>> from stage1_5_wwtp_dc.design import size_site
>>> out = size_site("wwtp_30mgd")
>>> out["pv"]["kwp"]
5706.0
>>> round(out["revenue_per_year_usd"]["0.10_per_mtoken"] / 1e6, 1)
25.6
"""
from __future__ import annotations
from typing import Any, Dict

from .archetypes import (
    ARCHETYPES,
    ARCHETYPE_LABELS,
    DC_UTILIZATION,
    PRICE_POINTS_USD_PER_MTOKEN,
)

SECONDS_PER_YEAR = 365 * 24 * 3600  # 31_536_000


def size_site(archetype_name: str) -> Dict[str, Any]:
    """Compute the full sizing report for one archetype.

    Parameters
    ----------
    archetype_name : str
        Key into `ARCHETYPES` (e.g. ``"wwtp_30mgd"``).

    Returns
    -------
    dict
        Nested dict with keys: ``site``, ``pv``, ``bess``, ``dc``, ``grid``,
        ``revenue_per_year_usd``, ``assumptions``. Every quantity is SI
        (kW, kWh, MWh, acres) unless noted.

    Raises
    ------
    KeyError
        If ``archetype_name`` is not registered in `ARCHETYPES`.
    """
    if archetype_name not in ARCHETYPES:
        raise KeyError(
            f"unknown archetype {archetype_name!r}; "
            f"known: {sorted(ARCHETYPES)}"
        )

    a = ARCHETYPES[archetype_name]

    # ── PV array ─────────────────────────────────────────────────────────────
    pv_land_acres = a["buffer_acres"] * a["pv_land_fraction"]
    pv_kwp = pv_land_acres * a["pv_density_kwp_per_acre"]
    pv_annual_mwh = pv_kwp * 8760 * a["pv_capacity_factor"] / 1000.0

    # ── WWTP baseline load ───────────────────────────────────────────────────
    wwtp_load_kw = a["mgd"] * a["wwtp_kw_per_mgd"]
    wwtp_grid_baseline_kw = max(wwtp_load_kw - a["biogas_offset_kw"], 0.0)

    # ── DC IT sizing (based on PV nameplate) ─────────────────────────────────
    dc_it_mw = a["dc_it_share_of_pv_dc"] * (pv_kwp / 1000.0)
    dc_facility_mw = dc_it_mw * a["pue"]
    racks = round(dc_it_mw * 1000.0 / a["rack_facility_kw"])
    tokens_per_sec = dc_it_mw * a["tokens_per_sec_per_mw"]

    # ── BESS sizing ──────────────────────────────────────────────────────────
    bess_mwh = dc_it_mw * a["bess_duration_hours"]                 # energy
    bess_max_discharge_kw = dc_it_mw * 1000.0                      # power
    bess_max_charge_kw = bess_max_discharge_kw * a["bess_charge_discharge_ratio"]

    # ── Grid-side impact ─────────────────────────────────────────────────────
    # Worst-case additional demand on the utility transformer: happens at
    # night with PV=0, BESS charging at full, DC at full load. WWTP baseline
    # is NOT double-counted (it was already on the feeder before the project).
    peak_added_kw = dc_facility_mw * 1000.0 + bess_max_charge_kw

    # ── Revenue at four price points ─────────────────────────────────────────
    # Realized tokens/year = nameplate × time-averaged utilization.
    realized_tokens_per_year = tokens_per_sec * SECONDS_PER_YEAR * DC_UTILIZATION
    realized_mtokens_per_year = realized_tokens_per_year / 1e6
    revenue_per_year_usd = {
        f"{p:.2f}_per_mtoken": realized_mtokens_per_year * p
        for p in PRICE_POINTS_USD_PER_MTOKEN
    }

    return {
        "archetype": archetype_name,
        "label": ARCHETYPE_LABELS[archetype_name],
        "site": {
            "mgd": a["mgd"],
            "buffer_acres": a["buffer_acres"],
            "wwtp_load_kw": round(wwtp_load_kw, 1),
            "wwtp_grid_baseline_kw": round(wwtp_grid_baseline_kw, 1),
            "biogas_offset_kw": a["biogas_offset_kw"],
        },
        "pv": {
            "kwp": round(pv_kwp, 1),
            "annual_mwh": round(pv_annual_mwh, 1),
            "land_used_acres": round(pv_land_acres, 2),
            "capacity_factor": a["pv_capacity_factor"],
        },
        "bess": {
            "mwh": round(bess_mwh, 2),
            "max_charge_kw": round(bess_max_charge_kw, 1),
            "max_discharge_kw": round(bess_max_discharge_kw, 1),
            "duration_hours": a["bess_duration_hours"],
        },
        "dc": {
            "it_load_mw": round(dc_it_mw, 3),
            "facility_load_mw": round(dc_facility_mw, 3),
            "racks": racks,
            "tokens_per_sec": tokens_per_sec,
            "utilization_factor": DC_UTILIZATION,
        },
        "grid": {
            "peak_added_kw": round(peak_added_kw, 1),
            "transformer_upgrade_required": peak_added_kw > 2000.0,
        },
        "revenue_per_year_usd": {k: round(v, 0) for k, v in revenue_per_year_usd.items()},
        "assumptions": {
            "pue": a["pue"],
            "dc_utilization": DC_UTILIZATION,
            "rack_facility_kw": a["rack_facility_kw"],
            "tokens_per_sec_per_mw": a["tokens_per_sec_per_mw"],
            "pv_density_kwp_per_acre": a["pv_density_kwp_per_acre"],
        },
    }


def size_all() -> Dict[str, Dict[str, Any]]:
    """Convenience: size every registered archetype. Returns {name: report}."""
    return {name: size_site(name) for name in ARCHETYPES}
