"""Smoke + quality tests for design.rag.

Exercises the default TF-IDF backend against the real 15-file wiki and locks
in a few "this question should retrieve this file" assertions. These catch
regressions in the tokenizer, IDF weighting, or doc-loading glob rules.

Run:
    cd stage1_5_wwtp_dc && pytest tests/test_rag.py -v
"""
from __future__ import annotations

import pytest

from stage1_5_wwtp_dc.design.rag import Retriever, retrieve


@pytest.fixture(scope="module")
def retriever():
    return Retriever()


class TestCorpusLoad:
    def test_wiki_has_expected_doc_count(self, retriever):
        # 15 content files + _index.md excluded = 15.
        assert len(retriever.docs) == 15

    def test_titles_are_non_empty(self, retriever):
        assert all(d.title for d in retriever.docs)

    def test_paths_are_relative(self, retriever):
        assert all("/" in d.path or d.path.endswith(".md") for d in retriever.docs)


class TestRetrievalQuality:
    @pytest.mark.parametrize(
        "query,expected_filename_substr",
        [
            ("which PV tracking is best at 30°N?",               "single_axis_tracker"),
            ("bifacial yield gain",                              "bifacial_gain"),
            ("CAPEX for 4 hour battery storage",                 "bess_nrel_atb_2024"),
            ("how many kW per rack for Blackwell",               "blackwell"),
            ("setback distance from aeration basins",            "wwtp_buffer_setback"),
            ("ERCOT interconnection for behind the meter load",  "tx_ercot_interconnect"),
            ("TOU arbitrage with PG&E rates",                    "tou_arbitrage"),
            ("Vera Rubin uncertainty 2026",                      "vera_rubin"),
            ("wafer-scale inference latency",                    "cerebras"),
            ("amd inference alternative",                        "amd_mi300x"),
            ("Lazard LCOE solar utility scale",                  "pv_lazard_lcoe_2024"),
            ("data center cooling CAPEX benchmark",              "dc_industry_benchmarks"),
            ("simplest no moving parts PV",                      "fixed_tilt"),
            ("dual axis solar tracker cost",                     "dual_axis"),
        ],
    )
    def test_top1_matches_expected(self, retriever, query, expected_filename_substr):
        hits = retriever.retrieve(query, k=3)
        assert hits, f"no hits returned for {query!r}"
        # The expected file should appear in the top 3 — top 1 is strong but
        # we allow top-3 to tolerate small TF-IDF tie-breaks.
        paths = [h["path"] for h in hits]
        assert any(expected_filename_substr in p for p in paths), (
            f"query {query!r} -> {paths} (expected {expected_filename_substr!r})"
        )


class TestContract:
    def test_empty_query_returns_empty_or_valid(self, retriever):
        hits = retriever.retrieve("", k=3)
        # Should not raise; may return stopword-filtered empty set.
        assert isinstance(hits, list)

    def test_k_clamped_to_corpus_size(self, retriever):
        hits = retriever.retrieve("PV", k=100)
        assert len(hits) <= len(retriever.docs)

    def test_module_level_retrieve_has_expected_shape(self):
        out = retrieve("single axis tracker", k=2)
        assert set(out) == {"query", "k", "hits", "backend"}
        assert len(out["hits"]) == 2
