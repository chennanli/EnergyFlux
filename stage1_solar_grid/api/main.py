"""
Sprint 6: FastAPI Integration — EnergyFlux Stage 1 API
=======================================================
REST API exposing all Stage 1 outputs:

  GET  /                → API info and available endpoints
  GET  /forecast        → 24h GHI forecast data
  GET  /generation      → PV AC power timeseries (4 modes)
  GET  /powerflow       → Bus voltages and line loading
  GET  /powerflow/summary → Voltage violation statistics
  POST /diagnose        → Trigger RCA agent with anomaly description

Usage:
  uvicorn stage1_solar_grid.api.main:app --reload --port 8000
  Then open http://localhost:8000/docs for interactive Swagger UI
"""

import os
import sys
import json
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# ── Paths ─────────────────────────────────────────────────────────────────────
STAGE1_DIR   = Path(__file__).parent.parent
PROJECT_ROOT = STAGE1_DIR.parent
DATA_DIR     = STAGE1_DIR / "data" / "processed"
RAW_DIR      = STAGE1_DIR / "data" / "raw"

load_dotenv(PROJECT_ROOT / ".env")

# ── Load data at startup ─────────────────────────────────────────────────────
def load_all_data():
    """Load all pre-computed data into memory."""
    data = {}

    # Forecast data
    forecast_path = DATA_DIR / "forecast_output.csv"
    if forecast_path.exists():
        data["forecast"] = pd.read_csv(forecast_path, index_col=0, parse_dates=True)

    # PV generation (4 modes)
    pv_path = DATA_DIR / "pv_comparison.csv"
    if pv_path.exists():
        df = pd.read_csv(pv_path, index_col=0)
        df.index = pd.to_datetime(df.index, utc=True)
        data["generation"] = df

    # Power flow results
    pf_path = DATA_DIR / "powerflow_results.csv"
    if pf_path.exists():
        df = pd.read_csv(pf_path, index_col=0)
        df.index = pd.to_datetime(df.index, utc=True)
        data["powerflow"] = df

    # Weather
    weather_path = RAW_DIR / "weather_fremont.csv"
    if weather_path.exists():
        data["weather"] = pd.read_csv(weather_path, index_col="timestamp", parse_dates=True)

    return data


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="EnergyFlux — Stage 1 API",
    description=(
        "Physics-informed solar energy platform API. "
        "Provides irradiance forecasting, PV generation modeling, "
        "power flow analysis, and AI-powered root cause analysis."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data on startup
DATA = {}

@app.on_event("startup")
async def startup():
    global DATA
    DATA = load_all_data()
    print(f"Data loaded: {list(DATA.keys())}")


# ── Models ────────────────────────────────────────────────────────────────────
class DiagnoseRequest(BaseModel):
    description: str
    """Anomaly description, e.g. 'PV bus voltage exceeded 1.05 pu at 2022-06-21 12:00'"""

class DiagnoseResponse(BaseModel):
    anomaly_type: Optional[str] = None
    severity: Optional[str] = None
    root_cause: Optional[str] = None
    evidence: Optional[list] = None
    recommended_actions: Optional[list] = None
    timestamp: Optional[str] = None
    raw_response: Optional[str] = None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """API info and available endpoints."""
    return {
        "name": "EnergyFlux Stage 1 API",
        "version": "1.0.0",
        "location": "Fremont, CA",
        "pv_capacity_kwp": 187.2,
        "bess_kw": 100,
        "bess_kwh": 400,
        "endpoints": {
            "GET /forecast": "24h GHI forecast data",
            "GET /generation": "PV AC power timeseries (4 modes)",
            "GET /powerflow": "Bus voltages, BESS status, load data",
            "GET /powerflow/summary": "Voltage violation statistics",
            "POST /diagnose": "Trigger RCA agent",
            "GET /docs": "Interactive Swagger UI",
        },
    }


@app.get("/forecast")
async def get_forecast(
    start: Optional[str] = Query(None, description="Start timestamp, e.g. 2022-06-21"),
    end: Optional[str] = Query(None, description="End timestamp, e.g. 2022-06-28"),
    limit: int = Query(168, description="Max rows to return (default 168 = 1 week)"),
):
    """Get GHI irradiance forecast data."""
    if "forecast" not in DATA:
        raise HTTPException(status_code=404, detail="Forecast data not available")

    df = DATA["forecast"]
    if start:
        df = df[df.index >= start]
    if end:
        df = df[df.index <= end]
    df = df[~df.index.duplicated(keep="first")].head(limit)

    return {
        "count": len(df),
        "unit": "W/m2",
        "data": json.loads(df.to_json(orient="index", date_format="iso")),
    }


@app.get("/generation")
async def get_generation(
    start: Optional[str] = Query(None, description="Start timestamp"),
    end: Optional[str] = Query(None, description="End timestamp"),
    mode: Optional[str] = Query(None, description="PV mode: 'fixed', 'no_backtrack', 'backtrack', 'bifacial'"),
    limit: int = Query(168, description="Max rows"),
):
    """Get PV AC power generation timeseries for all 4 modes."""
    if "generation" not in DATA:
        raise HTTPException(status_code=404, detail="Generation data not available")

    df = DATA["generation"]
    if start:
        df = df[df.index >= pd.Timestamp(start, tz="UTC")]
    if end:
        df = df[df.index <= pd.Timestamp(end, tz="UTC")]

    # Filter by mode if specified
    mode_map = {
        "fixed": "Fixed tilt 20 deg",
        "no_backtrack": "1P tracker (no backtrack)",
        "backtrack": "1P tracker + backtrack",
        "bifacial": "Bifacial + backtrack",
    }
    if mode and mode in mode_map:
        col = mode_map[mode]
        if col in df.columns:
            df = df[[col]]

    df = df.head(limit)

    # Annual summary
    full_df = DATA["generation"]
    summary = {}
    for col in full_df.columns:
        annual_mwh = full_df[col].sum() / 1000
        summary[col] = f"{annual_mwh:.0f} MWh/yr"

    return {
        "count": len(df),
        "unit": "kW",
        "annual_summary": summary,
        "data": json.loads(df.to_json(orient="index", date_format="iso")),
    }


@app.get("/powerflow")
async def get_powerflow(
    start: Optional[str] = Query(None, description="Start timestamp"),
    end: Optional[str] = Query(None, description="End timestamp"),
    limit: int = Query(168, description="Max rows"),
):
    """Get power flow results: bus voltages, BESS status, load data."""
    if "powerflow" not in DATA:
        raise HTTPException(status_code=404, detail="Power flow data not available")

    df = DATA["powerflow"]
    if start:
        df = df[df.index >= pd.Timestamp(start, tz="UTC")]
    if end:
        df = df[df.index <= pd.Timestamp(end, tz="UTC")]
    df = df.head(limit)

    return {
        "count": len(df),
        "columns": list(df.columns),
        "data": json.loads(df.to_json(orient="index", date_format="iso")),
    }


@app.get("/powerflow/summary")
async def get_powerflow_summary():
    """Get power flow summary statistics: voltage violations, line loading, BESS usage."""
    if "powerflow" not in DATA:
        raise HTTPException(status_code=404, detail="Power flow data not available")

    df = DATA["powerflow"]

    # Voltage columns
    v_cols = [c for c in df.columns if c.startswith("v_") and c != "v_MV Grid"]
    v_df = df[v_cols]

    # Voltage stats
    v_min = float(v_df.min().min())
    v_max = float(v_df.max().max())
    hours_over = int((v_df > 1.05).any(axis=1).sum())
    hours_under = int((v_df < 0.95).any(axis=1).sum())

    # BESS stats
    charge_kwh = float((-df["bess_kw"][df["bess_kw"] < 0]).sum())
    discharge_kwh = float(df["bess_kw"][df["bess_kw"] > 0].sum())

    return {
        "period": f"{df.index[0]} to {df.index[-1]}",
        "total_hours": len(df),
        "voltage": {
            "min_pu": round(v_min, 4),
            "max_pu": round(v_max, 4),
            "hours_overvoltage": hours_over,
            "hours_undervoltage": hours_under,
            "worst_bus": v_df.max().idxmax().replace("v_", ""),
        },
        "bess": {
            "total_charged_kwh": round(charge_kwh, 0),
            "total_discharged_kwh": round(discharge_kwh, 0),
            "soc_min_pct": round(float(df["soc"].min()) * 100, 0),
            "soc_max_pct": round(float(df["soc"].max()) * 100, 0),
        },
        "pv": {
            "peak_kw": round(float(df["pv_kw"].max()), 1),
            "annual_mwh": round(float(df["pv_kw"].sum()) / 1000, 1),
        },
    }


@app.post("/diagnose", response_model=DiagnoseResponse)
async def diagnose(request: DiagnoseRequest):
    """Trigger RCA agent to diagnose an anomaly."""
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="NVIDIA_API_KEY not configured")

    try:
        # Import agent components
        sys.path.insert(0, str(PROJECT_ROOT))
        from stage1_solar_grid.agent import rca_agent

        # Load data into agent module if not already loaded
        if rca_agent._pv_df is None:
            import importlib
            rca_agent._pv_df, rca_agent._pf_df, rca_agent._weather_df = rca_agent.load_data()
            rca_agent._vectorstore = rca_agent.build_vector_store()

        # Create agent and run
        llm_with_tools, tools = rca_agent.create_agent()
        result = rca_agent.run_rca(request.description, llm_with_tools, tools)

        # Try to parse JSON from response
        try:
            parsed = json.loads(result)
            return DiagnoseResponse(**parsed)
        except json.JSONDecodeError:
            return DiagnoseResponse(raw_response=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "stage1_solar_grid.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
