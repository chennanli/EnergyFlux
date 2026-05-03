"""pvlib-inspired PV array design tools, LLM-callable.

Scope
-----
Design-stage sizing only. Given land area, module choice, and tracking
technology, compute module count, string configuration, inverter count,
DC nameplate, and annual energy yield. **Not** 8,760-hour hourly simulation
(that's Blog 3, using pvlib.modelchain).

Why pure-Python (not pvlib) for the MVP
---------------------------------------
pvlib shines when you need TMY-hour-by-hour simulation, spectral mismatch,
or POA irradiance from plane-of-array geometry. For a *design-stage* tool
that answers "how many modules fit on 23 acres and how much energy do they
make in a year?", industry-standard lookup tables (NREL PVWatts v8 default
specific yields by latitude + tracking) are more honest than pretending to
run a 8,760-hour sim. Blog 3 will wrap pvlib for the real dynamic sim.

Each function below has a stable JSON-friendly signature so the NVIDIA NIM
LLM can treat it as a tool. Units are SI (acres for land by convention
because US WWTP parcels are always described in acres).

Sources
-------
* NREL PVWatts v8 documentation (specific-yield lookups)
* Lazard's LCOE+ 2024 (industry consensus on land density by tracking)
* SEIA Solar Industry Research Data (module efficiencies)
* Pure-Python: no external deps beyond numpy.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from math import ceil, floor
from typing import Literal, Dict, Any, List

# ---------------------------------------------------------------------------
# Constants (sources cited in module header)
# ---------------------------------------------------------------------------
ACRE_TO_M2 = 4046.8564224

#: Module catalog for Blog 2. These are representative products, not specific
#: vendor SKUs. Dimensions are typical for each wattage/technology.
MODULE_CATALOG: Dict[int, Dict[str, Any]] = {
    405: {
        "technology": "Mono PERC",
        "bifacial": False,
        "dimensions_m": (2.00, 1.00),
        "area_m2": 2.00,
        "efficiency_pct": 20.25,
        "note": "Budget-tier mono-facial; common in distributed-scale projects.",
    },
    500: {
        "technology": "TOPCon mono-facial",
        "bifacial": False,
        "dimensions_m": (2.28, 1.13),
        "area_m2": 2.58,
        "efficiency_pct": 19.4,
        "note": "Mid-tier TOPCon; better temp coefficient than PERC.",
    },
    580: {
        "technology": "TOPCon bifacial",
        "bifacial": True,
        "dimensions_m": (2.40, 1.20),
        "area_m2": 2.88,
        "efficiency_pct": 20.1,
        "note": "Utility-scale workhorse; +7% yield when deployed bifacial.",
    },
    625: {
        "technology": "HJT bifacial",
        "bifacial": True,
        "dimensions_m": (2.44, 1.22),
        "area_m2": 2.98,
        "efficiency_pct": 21.0,
        "note": "Premium HJT; best temp coef and degradation profile.",
    },
}

#: Land density (kWp-DC per acre) by tracking technology. Assumes modern
#: large-format bifacial or near-bifacial modules; GCR 0.30–0.40 typical.
#: Sources: Lazard LCOE+ 2024; NREL 2023 benchmark ground-mount reports.
KWP_PER_ACRE: Dict[str, float] = {
    "fixed_tilt":           290.0,
    "single_axis":          325.0,
    "single_axis_bifacial": 325.0,  # same geometry; bifacial gain is in yield
    "dual_axis":            180.0,
}

#: Specific yield lookup (kWh-AC / kWp-DC / year) by latitude zone and
#: tracking technology. Numbers aggregate NREL PVWatts v8 default runs for
#: representative US cities in each latitude band.
_SPECIFIC_YIELD: Dict[str, Dict[str, float]] = {
    # Southern US: Phoenix, Austin, Miami (lat < 30°N)
    "south": {
        "fixed_tilt":           1750.0,
        "single_axis":          2050.0,
        "single_axis_bifacial": 2200.0,
        "dual_axis":            2150.0,
    },
    # Central US: Nashville, Kansas City, DC (30°–38°N)
    "central": {
        "fixed_tilt":           1550.0,
        "single_axis":          1830.0,
        "single_axis_bifacial": 1960.0,
        "dual_axis":            1920.0,
    },
    # Northern US: Portland, Boston, Chicago (38°–45°N)
    "north": {
        "fixed_tilt":           1350.0,
        "single_axis":          1600.0,
        "single_axis_bifacial": 1720.0,
        "dual_axis":            1680.0,
    },
    # Far north: Seattle, Minneapolis, Montana (>45°N)
    "far_north": {
        "fixed_tilt":           1150.0,
        "single_axis":          1350.0,
        "single_axis_bifacial": 1450.0,
        "dual_axis":            1420.0,
    },
}


TrackingName = Literal[
    "fixed_tilt", "single_axis", "single_axis_bifacial", "dual_axis"
]


def _lat_zone(lat: float) -> str:
    """Map |latitude| (degrees) to one of four specific-yield zones."""
    abs_lat = abs(lat)
    if abs_lat < 30.0:
        return "south"
    if abs_lat < 38.0:
        return "central"
    if abs_lat < 45.0:
        return "north"
    return "far_north"


# ---------------------------------------------------------------------------
# Tool 1 — design_pv_array
# ---------------------------------------------------------------------------
@dataclass
class PVArrayDesign:
    kwp_dc: float
    module_count: int
    modules_per_string: int
    string_count: int
    tracking: str
    module_w: int
    bifacial: bool
    area_used_acres: float
    area_used_m2: float
    ilr: float
    inverter_count: int
    inverter_kw_each: int
    dimensions_m: Dict[str, float]
    notes: List[str]

    def as_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["kwp_dc"] = round(self.kwp_dc, 1)
        d["area_used_acres"] = round(self.area_used_acres, 2)
        d["area_used_m2"] = round(self.area_used_m2, 0)
        return d


def design_pv_array(
    area_acres: float,
    module_w: int = 580,
    tracking: TrackingName = "single_axis",
    bifacial: bool = True,
    ilr: float = 1.25,
    inverter_kw: int = 550,
) -> Dict[str, Any]:
    """Design a ground-mount PV array to fit a given parcel.

    Parameters
    ----------
    area_acres : float
        Buildable land area (acres). Access roads + inverter pads should
        already be subtracted; typical convention is 90% of buffer zone.
    module_w : int
        Nameplate module wattage (one of MODULE_CATALOG keys).
    tracking : str
        One of ``"fixed_tilt"``, ``"single_axis"``, ``"single_axis_bifacial"``,
        ``"dual_axis"``. If ``bifacial`` is True and ``tracking=="single_axis"``,
        it's promoted to ``"single_axis_bifacial"`` for yield purposes.
    bifacial : bool
        Use bifacial modules (affects yield; ``module_w`` must be a bifacial
        product for this to make physical sense).
    ilr : float
        DC-to-AC ratio (inverter loading ratio). 1.2–1.3 is industry norm.
    inverter_kw : int
        AC nameplate per central inverter. 550 kW is a common utility unit.

    Returns
    -------
    dict
        Array design summary (kWp, module count, strings, inverters, footprint).
    """
    if module_w not in MODULE_CATALOG:
        raise ValueError(
            f"module_w={module_w!r} not in MODULE_CATALOG; "
            f"choose from {sorted(MODULE_CATALOG)}"
        )
    if tracking not in KWP_PER_ACRE:
        raise ValueError(
            f"tracking={tracking!r} unknown; "
            f"choose from {sorted(KWP_PER_ACRE)}"
        )

    module = MODULE_CATALOG[module_w]

    # Promote single-axis + bifacial to the bifacial tracking profile for yield.
    eff_tracking = tracking
    if bifacial and tracking == "single_axis":
        eff_tracking = "single_axis_bifacial"

    # ─ Land-limited nameplate ────────────────────────────────────────────────
    kwp_max = area_acres * KWP_PER_ACRE[eff_tracking]

    # Round down to whole modules.
    module_count = floor(kwp_max * 1000 / module_w)
    kwp_dc = module_count * module_w / 1000.0
    area_used_m2 = area_acres * ACRE_TO_M2  # we use the allotted area

    # ─ String configuration ──────────────────────────────────────────────────
    # 1500 V DC systems typically allow 24–28 modules per string at Voc ≤ 1500 V.
    # 26 is the sweet spot with 580 W TOPCon-class modules.
    modules_per_string = 26
    string_count = ceil(module_count / modules_per_string)

    # ─ Inverter sizing ───────────────────────────────────────────────────────
    kwp_ac_needed = kwp_dc / ilr
    inverter_count = max(1, ceil(kwp_ac_needed / inverter_kw))

    # ─ Footprint (rough rectangle for viz) ───────────────────────────────────
    aspect = 2.0  # typical 2:1 W:D for utility PV parcels
    side_m = (area_used_m2 / aspect) ** 0.5
    dims = {"width_m": round(side_m * aspect, 0), "depth_m": round(side_m, 0)}

    notes = [
        f"Tracking: {eff_tracking} ({module['note']})",
        f"Density: {KWP_PER_ACRE[eff_tracking]:.0f} kWp/acre (Lazard/NREL consensus)",
        f"ILR: {ilr} (DC/AC ratio)",
    ]
    if bifacial and not module["bifacial"]:
        notes.append(
            f"⚠ bifacial=True but {module_w} W is mono-facial in the catalog — "
            f"no bifacial yield bonus will be counted."
        )

    return PVArrayDesign(
        kwp_dc=kwp_dc,
        module_count=module_count,
        modules_per_string=modules_per_string,
        string_count=string_count,
        tracking=eff_tracking,
        module_w=module_w,
        bifacial=bifacial and module["bifacial"],
        area_used_acres=area_acres,
        area_used_m2=area_used_m2,
        ilr=ilr,
        inverter_count=inverter_count,
        inverter_kw_each=inverter_kw,
        dimensions_m=dims,
        notes=notes,
    ).as_dict()


# ---------------------------------------------------------------------------
# Tool 2 — calc_annual_yield
# ---------------------------------------------------------------------------
def calc_annual_yield(
    kwp_dc: float,
    lat: float,
    tracking: TrackingName = "single_axis",
    bifacial: bool = True,
    performance_ratio: float = 0.82,
) -> Dict[str, Any]:
    """Estimate annual AC energy output from a DC nameplate and latitude.

    Uses NREL PVWatts-derived specific-yield tables (kWh/kWp/year) by
    latitude zone and tracking technology. The ``performance_ratio`` knob
    is exposed so engineers can override for soiling / snow loss estimates.

    Parameters
    ----------
    kwp_dc : float
        DC nameplate from ``design_pv_array``.
    lat : float
        Site latitude (degrees, positive north).
    tracking : str
        See ``design_pv_array``.
    bifacial : bool
        Promotes ``single_axis`` → ``single_axis_bifacial`` in the yield table.
    performance_ratio : float
        Overall system PR. 0.80–0.84 typical for ground mount.
        Defaults to 0.82 ≈ NREL PVWatts default after derate.

    Returns
    -------
    dict
        ``{annual_mwh, capacity_factor_pct, specific_yield_kwh_per_kwp, zone}``
    """
    if tracking not in KWP_PER_ACRE:
        raise ValueError(f"tracking={tracking!r} unknown")

    eff_tracking = tracking
    if bifacial and tracking == "single_axis":
        eff_tracking = "single_axis_bifacial"

    zone = _lat_zone(lat)
    ref_yield = _SPECIFIC_YIELD[zone][eff_tracking]

    # Scale from the table's baseline PR (~0.82) to user's PR.
    specific_yield = ref_yield * (performance_ratio / 0.82)
    annual_mwh = kwp_dc * specific_yield / 1000.0

    # Capacity factor = actual output / (nameplate × 8760 h)
    cf_pct = annual_mwh * 1000.0 / (kwp_dc * 8760.0) * 100.0

    return {
        "annual_mwh": round(annual_mwh, 1),
        "capacity_factor_pct": round(cf_pct, 2),
        "specific_yield_kwh_per_kwp": round(specific_yield, 1),
        "performance_ratio": performance_ratio,
        "zone": zone,
        "tracking_used": eff_tracking,
    }


# ---------------------------------------------------------------------------
# Tool 3 — compare_pv_technologies
# ---------------------------------------------------------------------------
def compare_pv_technologies(
    area_acres: float,
    lat: float,
    module_w: int = 580,
) -> Dict[str, Any]:
    """Return a side-by-side comparison across four tracking technologies.

    Useful as a single tool call when the LLM wants to help the user pick
    a tracking technology.

    Parameters
    ----------
    area_acres, lat : see above.
    module_w : int
        Module wattage to use for all four options (so comparison is fair).

    Returns
    -------
    dict
        ``{comparison: [ {tracking, kwp_dc, annual_mwh, cf_pct, ...}, ... ]}``
    """
    rows: List[Dict[str, Any]] = []
    for trk in ["fixed_tilt", "single_axis", "single_axis_bifacial", "dual_axis"]:
        bif = trk == "single_axis_bifacial"
        design = design_pv_array(
            area_acres=area_acres,
            module_w=module_w,
            tracking="single_axis" if bif else trk,
            bifacial=bif,
        )
        yld = calc_annual_yield(
            kwp_dc=design["kwp_dc"],
            lat=lat,
            tracking="single_axis" if bif else trk,
            bifacial=bif,
        )
        rows.append(
            {
                "tracking": trk,
                "kwp_dc": design["kwp_dc"],
                "module_count": design["module_count"],
                "annual_mwh": yld["annual_mwh"],
                "capacity_factor_pct": yld["capacity_factor_pct"],
                "specific_yield": yld["specific_yield_kwh_per_kwp"],
            }
        )
    return {
        "area_acres": area_acres,
        "lat": lat,
        "module_w": module_w,
        "zone": _lat_zone(lat),
        "comparison": rows,
    }


# ---------------------------------------------------------------------------
# Tool 4 — array_layout (for matplotlib viz)
# ---------------------------------------------------------------------------
def array_layout(design: Dict[str, Any]) -> Dict[str, Any]:
    """Produce a simple rectangular-parcel layout dict for viz.

    Takes the output of ``design_pv_array`` and returns (x, y, w, h) tuples
    for the overall parcel, the active array area, and inverter pads. The UI
    can then draw these rectangles with matplotlib.
    """
    w = design["dimensions_m"]["width_m"]
    d = design["dimensions_m"]["depth_m"]

    # Leave ~5% of the footprint for inverters/roads.
    inverter_strip_depth = max(10.0, 0.05 * d)
    array_depth = d - inverter_strip_depth

    return {
        "parcel": {"x": 0, "y": 0, "w": w, "h": d},
        "active_array": {"x": 0, "y": inverter_strip_depth, "w": w, "h": array_depth},
        "inverter_strip": {"x": 0, "y": 0, "w": w, "h": inverter_strip_depth},
        "labels": {
            "parcel": f"{design['area_used_acres']:.1f} ac",
            "array": f"{design['kwp_dc']:.0f} kWp DC",
            "inverters": f"{design['inverter_count']}× {design['inverter_kw_each']} kW",
        },
    }


# ---------------------------------------------------------------------------
# Tool schemas (for NIM/OpenAI-style tool calling)
# ---------------------------------------------------------------------------
TOOL_SCHEMAS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "design_pv_array",
            "description": (
                "Design a ground-mount PV array for a given parcel. "
                "Returns module count, string config, inverters, kWp DC, "
                "and footprint. Call this FIRST when sizing a new site."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "area_acres": {"type": "number",
                                   "description": "Buildable land area (acres, post-setback)"},
                    "module_w": {"type": "integer", "enum": [405, 500, 580, 625]},
                    "tracking": {"type": "string",
                                 "enum": ["fixed_tilt", "single_axis",
                                          "single_axis_bifacial", "dual_axis"]},
                    "bifacial": {"type": "boolean"},
                    "ilr": {"type": "number", "description": "DC/AC ratio, 1.2-1.3 typical"},
                    "inverter_kw": {"type": "integer",
                                    "description": "Per-inverter AC nameplate, 550 or 3125 kW"},
                },
                "required": ["area_acres"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calc_annual_yield",
            "description": (
                "Estimate annual AC energy output from a DC nameplate and "
                "site latitude. Uses NREL PVWatts specific-yield tables."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "kwp_dc": {"type": "number"},
                    "lat": {"type": "number"},
                    "tracking": {"type": "string",
                                 "enum": ["fixed_tilt", "single_axis",
                                          "single_axis_bifacial", "dual_axis"]},
                    "bifacial": {"type": "boolean"},
                    "performance_ratio": {"type": "number"},
                },
                "required": ["kwp_dc", "lat"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_pv_technologies",
            "description": (
                "Compare four PV tracking technologies (fixed, single-axis, "
                "single-axis bifacial, dual-axis) on the same parcel + latitude. "
                "Call this when the user asks 'which tracker should I use?'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "area_acres": {"type": "number"},
                    "lat": {"type": "number"},
                    "module_w": {"type": "integer", "enum": [405, 500, 580, 625]},
                },
                "required": ["area_acres", "lat"],
            },
        },
    },
]


#: Map tool name → callable, for the LLM dispatcher in design/llm.py.
TOOL_DISPATCH: Dict[str, Any] = {
    "design_pv_array": design_pv_array,
    "calc_annual_yield": calc_annual_yield,
    "compare_pv_technologies": compare_pv_technologies,
    "array_layout": array_layout,
}
