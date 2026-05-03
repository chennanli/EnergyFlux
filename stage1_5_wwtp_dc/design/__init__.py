"""design — parametric sizing module for the WWTP+PV+BESS+DC case study.

Exposes two things:

* `ARCHETYPES`  — a preset library of 30/40/50/60 MGD municipal WWTP sites.
* `size_site(name)` — a pure function that turns an archetype into a complete
  sizing report (PV kWp, BESS MWh, DC IT MW, rack count, tokens/s, annual
  revenue at four price points).

Design goals:

* No side effects; no I/O. Importable as a tool by the future Gemma
  orchestrator without dragging in Streamlit or file dependencies.
* Every derived quantity is traceable to one archetype scalar, so a reader of
  Blog 2 can see exactly which assumption drives which number.
* Existing model files in `stage1_5_wwtp_dc/models/` are untouched — this
  module wraps a thinner sizing layer on top.
"""
from .archetypes import ARCHETYPES, PRICE_POINTS_USD_PER_MTOKEN
from .sizing import size_site, size_all

__all__ = ["ARCHETYPES", "PRICE_POINTS_USD_PER_MTOKEN", "size_site", "size_all"]
