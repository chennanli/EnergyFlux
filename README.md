# EnergyFlux · 能流

<p align="center">
  <img src="logo.svg" width="500"/>
</p>

**Physics-informed analysis of industrial sites as hosts for behind-the-meter AI infrastructure.**

---

## Core Thesis

The bottleneck in AI infrastructure is often not chips. It is power delivery, siting, cooling, and permitting.

EnergyFlux asks a different question: can existing industrial sites host AI inference capacity behind the meter — reusing land that is already zoned, electrical infrastructure that is already connected, water and cooling that is already on-site, and operational staff that is already there?

The initial focus is on **MW-scale to tens-of-MW** deployments at industrial sites that already have most of the physical stack. Some larger industrial campuses can support larger deployments; the design logic changes at that scale and is covered in future case studies.

---

## Current Flagship Case Study

**`stage1_5_wwtp_dc/`** — Municipal wastewater treatment plant + solar + BESS + AI inference node

A 30 MGD WWTP is a strong first example because it combines, in one industrially-zoned parcel:
- mandatory buffer land (legally required to stay empty)
- existing MW-scale electrical service
- continuous treated water supply for liquid cooling
- 24/7 operations staff and physical security

This is one case study, not the full EnergyFlux thesis. WWTPs are not the only viable host site — they are a useful starting point because the combination of constraints is unusually complete.

→ See [`stage1_5_wwtp_dc/README.md`](stage1_5_wwtp_dc/README.md) for the full technical case study.

---

## What Is Implemented Today

| Module | Status | Location |
|---|---|---|
| WWTP case study: 8,760-hour annual simulation | ✅ Complete | `stage1_5_wwtp_dc/` |
| PV generation modeling (pvlib, real weather) | ✅ Complete | `stage1_5_wwtp_dc/models/pv_generator.py` |
| WWTP load model (QSDsan BSM1 ODE, default) | ✅ Complete | `stage1_5_wwtp_dc/models/wwtp_load_generator.py` |
| TOU-aware asymmetric BESS dispatch | ✅ Complete | `stage1_5_wwtp_dc/models/bess_dispatch.py` |
| Data center thermal ODE model | ✅ Complete | `stage1_5_wwtp_dc/models/dc_thermal.py` |
| Network / routing model | ✅ Complete | `stage1_5_wwtp_dc/models/network_model.py` |
| LLM anomaly RCA (NVIDIA NIM) | ✅ Complete | `stage1_5_wwtp_dc/agent/` |
| Streamlit dashboard | ✅ Complete | `stage1_5_wwtp_dc/app.py` |

## What Is Not Yet Built

| Item | Notes |
|---|---|
| Chemical plant case study | TEP-scale; planned as next case study |
| Generalized site screener | Needs more case studies before generalizing |
| Live accelerated dynamic simulator | Designed in PRD; not yet implemented |
| Multi-site economics / DCF model | Future work |

---

## Future Case Studies

- Chemical plants (EPA RMP setback zones, high internal AI demand)
- Larger industrial campuses and refineries (tens-of-MW scale, different permitting profile)
- Dedicated AI factory sites (purpose-built, different economics)

---

## Quick Start (WWTP Case Study)

```bash
git clone https://github.com/chennanli/EnergyFlux.git
cd EnergyFlux
python -m venv .venv && source .venv/bin/activate
pip install -r stage1_5_wwtp_dc/requirements.txt
cd stage1_5_wwtp_dc
PYTHONPATH=.. python run_demo.py --case all
streamlit run app.py
```

---

## Repo Structure

```
EnergyFlux/
├── README.md                    ← you are here (umbrella thesis)
├── docs/
│   ├── site_classes.md          ← industrial site-class screening matrix
│   ├── blog_series.md           ← blog series plan and positioning
│   └── roadmap.md               ← implemented vs planned
├── stage1_5_wwtp_dc/            ← flagship case study (this is where the code lives)
├── stage1_solar_grid/           ← Stage 1: early PV+grid exploration (locked, pre-thesis)
├── stage2_bess_ems/             ← Stage 2: early BESS scratch work (pre-thesis, retained for reference)
├── stage3_consumption/          ← Stage 3: early consumption scratch (pre-thesis, retained for reference)
├── configs/
└── tests/
```

Blog drafts and internal planning docs live in `blog/` and `_internal/` (both gitignored — local only).

---

## Author

[Chennan Li](https://linkedin.com/in/chennanli), PhD, PE
~20 years in industrial AI and energy systems — GE, AspenTech, NEXTracker, Schneider Electric.

---

## License

MIT
