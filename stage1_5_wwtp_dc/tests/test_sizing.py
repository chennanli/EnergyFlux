"""Regression tests for design.sizing — locks the 30 MGD case to Blog 1's
published numbers so refactors can't silently break the headline figures.

Run locally:
    cd stage1_5_wwtp_dc && pytest tests/test_sizing.py -v
"""
from __future__ import annotations
import pytest

from stage1_5_wwtp_dc.design import ARCHETYPES, size_site, size_all


# ---------------------------------------------------------------------------
# 30 MGD case — the numbers that shipped in Blog 1.
# If any of these fail, double-check the blog + archetype assumptions.
# ---------------------------------------------------------------------------
class Test30MGD:
    def setup_method(self):
        self.out = size_site("wwtp_30mgd")

    def test_pv_kwp_matches_blog1(self):
        # Blog 1 headline: 5,700 kWp PV.
        # Archetype math: 20 ac × 0.90 × 317 kWp/ac = 5706 kWp. Within 0.2%.
        assert self.out["pv"]["kwp"] == pytest.approx(5706.0, rel=0.005)

    def test_pv_annual_generation_in_band(self):
        # Blog 1 references ~10,660 MWh/yr; tolerate ±5% for derate variance.
        assert self.out["pv"]["annual_mwh"] == pytest.approx(10660.0, rel=0.05)

    def test_dc_it_load_is_2_mw(self):
        assert self.out["dc"]["it_load_mw"] == pytest.approx(2.0, rel=0.01)

    def test_racks_is_16(self):
        # 2 MW / 125 kW per Blackwell NVL72 rack = 16.
        assert self.out["dc"]["racks"] == 16

    def test_bess_is_8_mwh(self):
        # 2 MW DC × 4-hour BESS = 8 MWh.
        assert self.out["bess"]["mwh"] == pytest.approx(8.0, rel=0.01)

    def test_tokens_per_sec_is_116e6(self):
        # 2 MW × 5.8e6 tokens/s per MW (Blackwell FP8) = 11.6e6.
        assert self.out["dc"]["tokens_per_sec"] == pytest.approx(1.16e7, rel=0.01)

    def test_revenue_at_010_per_mtoken_in_25m_band(self):
        # At $0.10 / M tokens, 70% utilization, 2 MW DC → ~$25M/yr.
        r = self.out["revenue_per_year_usd"]["0.10_per_mtoken"]
        assert 23_000_000 <= r <= 28_000_000, f"${r:,}"

    def test_transformer_upgrade_flag_set(self):
        assert self.out["grid"]["transformer_upgrade_required"] is True


# ---------------------------------------------------------------------------
# Cross-archetype monotonicity: every sizing metric should grow with MGD.
# This catches regressions where a formula breaks for non-base archetypes.
# ---------------------------------------------------------------------------
class TestArchetypeMonotonicity:
    def setup_method(self):
        self.reports = size_all()
        # Sort by MGD so we can walk up the list.
        self.in_mgd_order = sorted(
            self.reports.values(), key=lambda r: r["site"]["mgd"]
        )

    @pytest.mark.parametrize(
        "path",
        [
            ("pv", "kwp"),
            ("pv", "annual_mwh"),
            ("bess", "mwh"),
            ("dc", "it_load_mw"),
            ("dc", "tokens_per_sec"),
            ("grid", "peak_added_kw"),
            ("site", "wwtp_load_kw"),
        ],
    )
    def test_metric_is_monotonic_in_mgd(self, path):
        values = []
        for r in self.in_mgd_order:
            v = r
            for k in path:
                v = v[k]
            values.append(v)
        for earlier, later in zip(values, values[1:]):
            assert later > earlier, (
                f"{'/'.join(path)} non-monotonic: {values}"
            )


# ---------------------------------------------------------------------------
# Contract: size_site must return a dict with the keys Blog 2 / the
# orchestrator depend on. Locks the public schema.
# ---------------------------------------------------------------------------
def test_report_schema_is_stable():
    out = size_site("wwtp_30mgd")
    expected_top = {
        "archetype", "label", "site", "pv", "bess", "dc", "grid",
        "revenue_per_year_usd", "assumptions",
    }
    assert set(out) == expected_top

    # Revenue keys: one per price point in archetypes.PRICE_POINTS.
    assert set(out["revenue_per_year_usd"]) == {
        "0.05_per_mtoken", "0.10_per_mtoken",
        "0.20_per_mtoken", "0.30_per_mtoken",
    }


def test_unknown_archetype_raises():
    with pytest.raises(KeyError):
        size_site("wwtp_999mgd_lol")


def test_all_archetypes_report_sane_revenue():
    # At $0.05 per M tokens (pessimistic), the smallest site still clears $10M.
    for name, report in size_all().items():
        r = report["revenue_per_year_usd"]["0.05_per_mtoken"]
        assert r > 10_000_000, f"{name} floor revenue too low: ${r:,}"
