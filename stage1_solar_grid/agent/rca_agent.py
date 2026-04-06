"""
Sprint 5: Root Cause Analysis Agent — NVIDIA NIM + LangChain ReAct
===================================================================
ReAct agent powered by Nemotron-Ultra (via NVIDIA NIM API) that diagnoses
anomalies in the solar PV + grid system.

Triggers:
  1. PV output deviates > 15% from forecast
  2. Bus voltage exceeds ANSI C84.1 limits (0.95-1.05 pu)
  3. Line loading exceeds 80%

Tools:
  - query_weather: fetch current weather conditions
  - query_powerflow: get bus voltages and line loading
  - query_pv_status: get PV generation vs expected
  - query_knowledge_base: RAG search over engineering documents

Output: structured RCA report (JSON)

Usage:
  python stage1_solar_grid/agent/rca_agent.py
"""

import os
import json
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from pathlib import Path
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT_ROOT  = Path(__file__).parent.parent.parent
STAGE1_DIR    = Path(__file__).parent.parent
KB_DIR        = Path(__file__).parent / "knowledge_base"
PV_CSV        = STAGE1_DIR / "data" / "processed" / "pv_comparison.csv"
PF_CSV        = STAGE1_DIR / "data" / "processed" / "powerflow_results.csv"
WEATHER_CSV   = STAGE1_DIR / "data" / "raw" / "weather_fremont.csv"

# ── Load env ──────────────────────────────────────────────────────────────────
load_dotenv(PROJECT_ROOT / ".env")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")


# ── Build RAG vector store ───────────────────────────────────────────────────
def build_vector_store():
    """Load knowledge base documents and create FAISS vector store."""
    loader = DirectoryLoader(
        str(KB_DIR), glob="**/*.md",
        loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"},
    )
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
    )
    vectorstore = FAISS.from_documents(chunks, embeddings)
    print(f"Knowledge base loaded: {len(docs)} docs → {len(chunks)} chunks")
    return vectorstore


# ── Load data ────────────────────────────────────────────────────────────────
def load_data():
    """Load PV, powerflow, and weather data."""
    pv_df = pd.read_csv(PV_CSV, index_col=0)
    pv_df.index = pd.to_datetime(pv_df.index, utc=True)

    pf_df = pd.read_csv(PF_CSV, index_col=0)
    pf_df.index = pd.to_datetime(pf_df.index, utc=True)

    weather_df = pd.read_csv(WEATHER_CSV, index_col="timestamp", parse_dates=True)

    return pv_df, pf_df, weather_df


# ── Tool definitions ─────────────────────────────────────────────────────────
# These will be populated with data after loading
_pv_df = None
_pf_df = None
_weather_df = None
_vectorstore = None


@tool
def query_weather(timestamp: str) -> str:
    """Query weather conditions at a specific timestamp.
    Args:
        timestamp: ISO format timestamp, e.g. '2022-06-21 12:00'
    Returns:
        Weather data including GHI, DNI, temperature, cloud cover, wind speed.
    """
    try:
        ts = pd.Timestamp(timestamp)
        # Find closest timestamp in weather data
        idx = _weather_df.index.get_indexer([ts], method="nearest")[0]
        row = _weather_df.iloc[idx]
        return json.dumps({
            "timestamp": str(_weather_df.index[idx]),
            "ghi_wm2": float(row["ghi_wm2"]),
            "dni_wm2": float(row["dni_wm2"]),
            "dhi_wm2": float(row["dhi_wm2"]),
            "temp_c": float(row["temp_c"]),
            "cloud_pct": float(row["cloud_pct"]),
            "humidity_pct": float(row["humidity_pct"]),
            "wind_ms": float(row["wind_ms"]),
        })
    except Exception as e:
        return f"Error querying weather: {e}"


@tool
def query_pv_status(timestamp: str) -> str:
    """Query PV generation status at a specific timestamp.
    Args:
        timestamp: ISO format timestamp, e.g. '2022-06-21 12:00'
    Returns:
        PV generation data for all 4 modes, plus BESS status.
    """
    try:
        ts = pd.Timestamp(timestamp, tz="UTC")
        # Find closest timestamp
        idx = _pv_df.index.get_indexer([ts], method="nearest")[0]
        pv_row = _pv_df.iloc[idx]

        pf_idx = _pf_df.index.get_indexer([ts], method="nearest")[0]
        pf_row = _pf_df.iloc[pf_idx]

        result = {
            "timestamp": str(_pv_df.index[idx]),
            "pv_modes": {},
            "bess_kw": float(pf_row.get("bess_kw", 0)),
            "bess_soc": float(pf_row.get("soc", 0)),
            "total_load_kw": float(pf_row.get("total_load_kw", 0)),
        }
        for col in _pv_df.columns:
            result["pv_modes"][col] = float(pv_row[col])
        return json.dumps(result)
    except Exception as e:
        return f"Error querying PV status: {e}"


@tool
def query_powerflow(timestamp: str) -> str:
    """Query power flow results (bus voltages, line loading) at a specific timestamp.
    Args:
        timestamp: ISO format timestamp, e.g. '2022-06-21 12:00'
    Returns:
        Bus voltages (pu) and key grid metrics.
    """
    try:
        ts = pd.Timestamp(timestamp, tz="UTC")
        idx = _pf_df.index.get_indexer([ts], method="nearest")[0]
        row = _pf_df.iloc[idx]

        voltages = {}
        for col in _pf_df.columns:
            if col.startswith("v_"):
                bus_name = col[2:]  # remove "v_" prefix
                voltages[bus_name] = float(row[col])

        # Find voltage violations
        violations = []
        for bus, v in voltages.items():
            if v > 1.05:
                violations.append(f"{bus}: {v:.4f} pu (OVERVOLTAGE)")
            elif v < 0.95:
                violations.append(f"{bus}: {v:.4f} pu (UNDERVOLTAGE)")

        return json.dumps({
            "timestamp": str(_pf_df.index[idx]),
            "bus_voltages_pu": voltages,
            "violations": violations,
            "pv_kw": float(row.get("pv_kw", 0)),
            "bess_kw": float(row.get("bess_kw", 0)),
            "total_load_kw": float(row.get("total_load_kw", 0)),
        })
    except Exception as e:
        return f"Error querying power flow: {e}"


@tool
def query_knowledge_base(query: str) -> str:
    """Search the engineering knowledge base for relevant information.
    Args:
        query: natural language question about PV system, grid, or troubleshooting
    Returns:
        Relevant excerpts from engineering documents.
    """
    try:
        results = _vectorstore.similarity_search(query, k=3)
        texts = []
        for doc in results:
            source = Path(doc.metadata.get("source", "unknown")).name
            texts.append(f"[{source}]\n{doc.page_content}")
        return "\n\n---\n\n".join(texts)
    except Exception as e:
        return f"Error searching knowledge base: {e}"


# ── Create agent ─────────────────────────────────────────────────────────────
def create_agent():
    """Create the ReAct RCA agent with NVIDIA NIM backend."""
    llm = ChatOpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        model="nvidia/llama-3.1-nemotron-ultra-253b-v1",
        api_key=NVIDIA_API_KEY,
        temperature=0.3,
        max_tokens=2048,
    )

    tools = [query_weather, query_pv_status, query_powerflow, query_knowledge_base]
    llm_with_tools = llm.bind_tools(tools)

    return llm_with_tools, tools


# ── Run RCA ──────────────────────────────────────────────────────────────────
def run_rca(anomaly_description: str, llm_with_tools, tools):
    """
    Run root cause analysis for a given anomaly.
    Uses a simple ReAct loop: LLM decides which tools to call,
    executes them, feeds results back, until it has enough info.
    """
    system_prompt = """You are an expert solar PV and grid engineer performing root cause analysis.

You have access to tools to query weather, PV generation, power flow data, and an engineering knowledge base.

When given an anomaly description:
1. First query relevant data to understand the situation
2. Check weather conditions at the time of the anomaly
3. Check PV generation and power flow status
4. Search the knowledge base for relevant troubleshooting info
5. Synthesize findings into a structured diagnosis

Your final response MUST be a JSON object with this structure:
{
    "anomaly_type": "overvoltage | undervoltage | low_generation | overloading | bess_issue",
    "severity": "low | medium | high | critical",
    "root_cause": "clear one-sentence explanation",
    "evidence": ["list of key data points supporting the diagnosis"],
    "recommended_actions": ["list of specific actions to resolve"],
    "timestamp": "when the anomaly occurred"
}
"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=anomaly_description),
    ]

    # Build tool lookup
    tool_map = {t.name: t for t in tools}

    # ReAct loop (max 5 iterations)
    for iteration in range(5):
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        # Check for tool calls
        if response.tool_calls:
            for tc in response.tool_calls:
                tool_name = tc["name"]
                tool_args = tc["args"]
                print(f"  → Calling {tool_name}({tool_args})")

                if tool_name in tool_map:
                    result = tool_map[tool_name].invoke(tool_args)
                else:
                    result = f"Unknown tool: {tool_name}"

                from langchain_core.messages import ToolMessage
                messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))
        else:
            # No tool calls — agent is done
            break

    return response.content


# ── Demo scenarios ───────────────────────────────────────────────────────────
DEMO_SCENARIOS = [
    {
        "name": "Midday Overvoltage",
        "description": (
            "Alert: Bus voltage at PV Plant exceeded 1.05 pu at 2022-06-21 12:00. "
            "Current reading is 1.068 pu. BESS SOC is at 90%. "
            "Please diagnose the root cause and recommend actions."
        ),
    },
    {
        "name": "Low PV Output on Clear Day",
        "description": (
            "Alert: PV output at 2022-07-15 11:00 is only 85 kW, "
            "which is 37% below the expected 135 kW for clear sky conditions. "
            "Weather station shows clear sky. "
            "Please investigate the root cause."
        ),
    },
    {
        "name": "Evening Voltage Dip",
        "description": (
            "Alert: Bus voltage at Chemical Plant dropped to 0.972 pu at 2022-12-15 18:00. "
            "PV generation is 0 kW (sunset). EV charging load is at peak. "
            "BESS SOC is at 12%. Please diagnose and recommend actions."
        ),
    },
]


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("EnergyFlux — Root Cause Analysis Agent")
    print("Model: NVIDIA Nemotron-Ultra (via NIM API)")
    print("=" * 60)

    # Load data into module-level variables used by tools
    import sys
    _mod = sys.modules[__name__]
    _mod._pv_df, _mod._pf_df, _mod._weather_df = load_data()
    _mod._vectorstore = build_vector_store()

    # Create agent
    llm_with_tools, tools = create_agent()
    print("Agent ready.\n")

    # Run demo scenario
    # Run all demo scenarios
    import sys
    scenario_idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    scenario = DEMO_SCENARIOS[scenario_idx]
    print(f"── Scenario: {scenario['name']} ──")
    print(f"Input: {scenario['description']}\n")
    print("Agent thinking...\n")

    result = run_rca(scenario["description"], llm_with_tools, tools)

    print("\n── RCA Report ──")
    print(result)
