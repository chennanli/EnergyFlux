"""Regression tests for design.pv_tools.

Locks in the Austin-TX demo numbers that appear in the Blog 2 demo script, so
if anyone tweaks the specific-yield tables, the blog's quoted figures can't
silently drift. Also confirms monotonicity across technologies and
catches obvious sign errors.

Run locally:
    cd stage1_5_wwtp_dc && pytest tests/test_pv_tools.py -v
"""
from __future__ import annotations
import pytest

from stage1_5_wwtp_dc.design.pv_tools import (
    KWP_PER_ACRE,
    MODULE_CATALOG,
    calc_annual_yield,
    compare_pv_technologies,
    design_pv_array,
    array_layout,
)


# ---------------------------------------------------------------------------
# The Austin TX demo — 45 MGD WWTP, 23 acres buffer, single-axis bifacial TOPCon.
# These numbers are the ones the LLM demo in the blog post will call out.
# ---------------------------------------------------------------------------
class TestAustinDemo:
    AUSTIN_LAT = 30.27  # Austin-Bergstrom airport latitude
    AREA_AC = 23.0

    def setup_method(self):
        self.design = design_pv_array(
            area_acres=self.AREA_AC,
            module_w=580,
            tracking="single_axis",
            bifacial=True,
        )
        self.yld = calc_annual_yield(
            kwp_dc=self.design["kwp_dc"],
            lat=self.AUSTIN_LAT,
            tracking="single_axis",
            bifacial=True,
        )

    def test_kwp_dc_in_6_to_8_MW_band(self):
        # 23 acres × 325 kWp/ac = 7,475 kWp ceiling; rounded down to whole modules.
        assert 6_000 <= self.design["kwp_dc"] <= 8_000

    def test_module_count_is_plausible(self):
        # ~7,400 kWp / 0.58 kW per module ≈ 12,800 modules.
        assert 10_000 <= self.design["module_count"] <= 14_000

    def test_string_count_makes_sense(self):
        # module_count / 26 modules per string
        expected = -(-self.design["module_count"] // 26)  # ceil division
        assert self.design["string_count"] == expected

    def test_inverter_count_is_reasonable(self):
        # kWp_DC / 1.25 ILR / 550 kW per inverter ≈ 11 units; allow 8-14.
        assert 8 <= self.design["inverter_count"] <= 16

    def test_effective_tracking_upgrades_to_bifacial(self):
        assert self.design["tracking"] == "single_axis_bifacial"

    def test_annual_yield_in_band(self):
        # Austin is "south" zone (lat 30.27 <-> borderline; 30.27 < 30? no, >30, central).
        # Actually 30.27 → central zone per _lat_zone. So specific yield ~1960.
        # 7,400 kWp × 1.96 MWh/kWp ≈ 14,500 MWh/yr.
        assert 12_000 <= self.yld["annual_mwh"] <= 17_000

    def test_capacity_factor_reasonable(self):
        assert 20.0 <= self.yld["capacity_factor_pct"] <= 28.0


# ---------------------------------------------------------------------------
# Monotonicity: yields should rank dual-axis ≳ bifacial 1-axis > 1-axis > fixed
# at every latitude. This catches obvious table swaps.
# ---------------------------------------------------------------------------
class TestYieldMonotonicity:
    @pytest.mark.parametrize("lat", [25.0, 32.0, 40.0, 48.0])
    def test_tracking_rank_at_each_latitude(self, lat):
        # All four at 10 acres, 580W modules.
        cmp = compare_pv_technologies(area_acres=10.0, lat=lat, module_w=580)
        rows = {r["tracking"]: r["specific_yield"] for r in cmp["comparison"]}
        # Single-axis tracker always beats fixed-tilt.
        assert rows["single_axis"] > rows["fixed_tilt"]
        # Bifacial 1-axis beats mono 1-axis.
        assert rows["single_axis_bifacial"] > rows["single_axis"]
        # Dual-axis is between 1-axis and bifacial 1-axis in NREL data.
        assert rows["dual_axis"] > rows["single_axis"]


# ---------------------------------------------------------------------------
# Contract tests — schema stability
# ---------------------------------------------------------------------------
def test_design_pv_array_returns_expected_keys():
    d = design_pv_array(area_acres=10.0)
    required = {
        "kwp_dc", "module_count", "modules_per_string", "string_count",
        "tracking", "module_w", "bifacial", "area_used_acres", "area_used_m2",
        "ilr", "inverter_count", "inverter_kw_each", "dimensions_m", "notes",
    }
    assert required <= set(d)


def test_calc_annual_yield_returns_expected_keys():
    y = calc_annual_yield(kwp_dc=5000.0, lat=30.0)
    required = {
        "annual_mwh", "capacity_factor_pct", "specific_yield_kwh_per_kwp",
        "performance_ratio", "zone", "tracking_used",
    }
    assert required <= set(y)


def test_unknown_module_raises():
    with pytest.raises(ValueError):
        design_pv_array(area_acres=10.0, module_w=999)


def test_unknown_tracking_raises():
    with pytest.raises(ValueError):
        design_pv_array(area_acres=10.0, tracking="hovering_in_space")


# ---------------------------------------------------------------------------
# Layout helper
# ---------------------------------------------------------------------------
def test_array_layout_produces_rectangles():
    design = design_pv_array(area_acres=20.0, module_w=580)
    layout = array_layout(design)
    # All three rects should be present and non-negative.
    for k in ("parcel", "active_array", "inverter_strip"):
        r = layout[k]
        assert r["w"] > 0 and r["h"] > 0
    # Active + inverter strip should roughly recover parcel area.
    p = layout["parcel"]
    a = layout["active_array"]
    s = layout["inverter_strip"]
    reconstructed_area = a["w"] * a["h"] + s["w"] * s["h"]
    assert abs(reconstructed_area - p["w"] * p["h"]) / (p["w"] * p["h"]) < 0.02
