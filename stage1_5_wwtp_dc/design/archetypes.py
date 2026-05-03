"""Archetype presets for parametric sizing.

Each archetype is a frozen dictionary of the *input* parameters that uniquely
define a site. Derived quantities (PV kWp, BESS MWh, revenue, ...) are
computed by `sizing.size_site()` from these inputs — nothing is pre-baked.

Why 30/40/50/60 MGD and not a continuous slider?
----------------------------------------------
Blog 1's revenue table covered exactly these four municipal WWTP sizes
because AWWA utility benchmarking data clusters around them — roughly 70%
of US WWTPs serving 50k–500k people fall in the 25–75 MGD band. A continuous
slider gives false precision (intermediate sites don't actually exist in
that population); discrete archetypes match the real distribution.

All "base" constants are traceable:
* WWTP kW/MGD        — derived from BSM1-calibrated stage1_5 sim @ 30 MGD.
* PV density kWp/ac  — typical for single-axis tracker, fixed tilt rural site.
* PV capacity factor — ERCOT/Southwest 2024 PVlib actuals.
* Rack kW            — Blackwell GB200 NVL72 per-rack facility draw.
* Tokens/s per MW    — per-MW inference throughput, Blackwell tensor core FP8.
"""
from __future__ import annotations
from typing import Mapping

# ---------------------------------------------------------------------------
# Shared constants across archetypes
# ---------------------------------------------------------------------------
PRICE_POINTS_USD_PER_MTOKEN: tuple[float, ...] = (0.05, 0.10, 0.20, 0.30)

# Time-averaged DC loading fraction (fraction of nameplate IT load actually
# drawn over the year). 0.70 is consistent with "steady inference serving"
# workload profiles where the queue rarely empties.
DC_UTILIZATION = 0.70


def _build_wwtp_archetype(
    *,
    mgd: float,
    buffer_acres: float,
    wwtp_kw_per_mgd: float = 83.33,  # 2500 kW / 30 MGD baseline
    biogas_offset_kw: float = 800.0,  # CHP constant, typical for >25 MGD plants
    pv_density_kwp_per_acre: float = 317.0,  # ground-mount single-axis
    pv_land_fraction: float = 0.90,   # 10% for access roads, inverter pads
    pv_capacity_factor: float = 0.214,  # Southwest 2024 actuals
    bess_duration_hours: float = 4.0,  # "4-hour battery" industry norm
    bess_charge_discharge_ratio: float = 0.5,  # max_charge / max_discharge
    dc_it_share_of_pv_dc: float = 0.35,  # DC IT MW = 0.35 × PV MWp
    pue: float = 1.25,                 # modern liquid-cooled facility
    rack_facility_kw: float = 125.0,   # Blackwell GB200 NVL72 per rack
    tokens_per_sec_per_mw: float = 5.8e6,  # Blackwell FP8
) -> dict:
    """Assemble one archetype dict. Every number has a named parameter so a
    reader of the blog can see the provenance of each assumption."""
    return {
        "mgd": mgd,
        "buffer_acres": buffer_acres,
        "wwtp_kw_per_mgd": wwtp_kw_per_mgd,
        "biogas_offset_kw": biogas_offset_kw,
        "pv_density_kwp_per_acre": pv_density_kwp_per_acre,
        "pv_land_fraction": pv_land_fraction,
        "pv_capacity_factor": pv_capacity_factor,
        "bess_duration_hours": bess_duration_hours,
        "bess_charge_discharge_ratio": bess_charge_discharge_ratio,
        "dc_it_share_of_pv_dc": dc_it_share_of_pv_dc,
        "pue": pue,
        "rack_facility_kw": rack_facility_kw,
        "tokens_per_sec_per_mw": tokens_per_sec_per_mw,
    }


# ---------------------------------------------------------------------------
# The four municipal WWTP archetypes
# ---------------------------------------------------------------------------
# Buffer acreage scales with MGD but sub-linearly: larger plants have
# proportionally less land-per-MGD because the treatment footprint grows
# slower than influent flow (process intensification).
# Rule used here: buffer_acres ≈ 0.67 × MGD^0.95.
ARCHETYPES: Mapping[str, dict] = {
    "wwtp_30mgd": _build_wwtp_archetype(
        mgd=30.0,
        buffer_acres=20.0,   # matches stage1_5 sim @ 30 MGD (PRD spec)
    ),
    "wwtp_40mgd": _build_wwtp_archetype(
        mgd=40.0,
        buffer_acres=26.0,   # 0.67 × 40^0.95 ≈ 25.9
    ),
    "wwtp_50mgd": _build_wwtp_archetype(
        mgd=50.0,
        buffer_acres=32.0,   # 0.67 × 50^0.95 ≈ 31.9
    ),
    "wwtp_60mgd": _build_wwtp_archetype(
        mgd=60.0,
        buffer_acres=38.0,   # 0.67 × 60^0.95 ≈ 38.0
    ),
}


# ---------------------------------------------------------------------------
# Display-friendly labels (used by Streamlit dropdown and tables)
# ---------------------------------------------------------------------------
ARCHETYPE_LABELS: Mapping[str, str] = {
    "wwtp_30mgd": "30 MGD municipal WWTP",
    "wwtp_40mgd": "40 MGD municipal WWTP",
    "wwtp_50mgd": "50 MGD municipal WWTP",
    "wwtp_60mgd": "60 MGD municipal WWTP",
}
