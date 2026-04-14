"""Stage 1.5 Step 8 — Dispatch agent with rule-based routing + LLM RCA.

Uses NVIDIA NIM via NVIDIA_API_KEY from .env.
Falls back to mock if key not set. Matches Stage 1's LLM pattern.

Model: meta/llama-3.1-8b-instruct (fast, free-tier friendly)
Timeout: 15s to prevent hanging during demo runs.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from agent.rca_prompts import ANOMALY_TEMPLATES, WWTP_DC_RCA_PROMPT

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

SOC_MAX_KWH = 7600.0  # 95% × 8,000 kWh — matches bess_dispatch.py

# Use a fast model for demos. Nemotron-Ultra (253B) is too slow for 24-step loops.
# Switch to Nemotron-Ultra only for single-query deep analysis.
NIM_MODEL = "meta/llama-3.1-8b-instruct"
NIM_TIMEOUT = 15  # seconds — prevents hanging if API is slow


def _detect_anomalies(state: dict) -> list[str]:
    anomalies = []
    if state["T_chip"] > 78:
        anomalies.append("thermal")
    if state["P_wwtp"] > 2800:
        anomalies.append("wwtp_overload")
    if state["bess_soc"] < 12:
        # Threshold 12% = SOC_MIN (10%) + 2% buffer.
        # bess_dispatch targets ~10-15% SOC at end of evening discharge — by design.
        # Do NOT set threshold at 15%; that fires every night as normal operation.
        anomalies.append("bess_low")
    if state["api_latency"] > 300:
        anomalies.append("api_congestion")
    if state.get("balance_error", 0) > 0.01:
        anomalies.append("energy_violation")
    return anomalies


def _call_llm(prompt: str) -> str:
    api_key = os.environ.get("NVIDIA_API_KEY", "")
    if not api_key:
        return "[MOCK RCA] No NVIDIA_API_KEY set. In production, NVIDIA NIM would analyze this anomaly and provide physics-grounded root cause analysis with recommended actions."
    try:
        from openai import OpenAI

        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key,
            timeout=NIM_TIMEOUT,
        )
        completion = client.chat.completions.create(
            model=NIM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,     # shorter for demo speed
            temperature=0.3,
        )
        msg = completion.choices[0].message
        content = msg.content or ""
        if hasattr(msg, "reasoning_content") and msg.reasoning_content:
            content = msg.reasoning_content + "\n\n" + content
        return content.strip() if content.strip() else "[NIM RCA] Model returned empty response."
    except Exception as exc:
        return f"[MOCK RCA] NIM call failed ({type(exc).__name__}): {exc}"


def _route_decision(T_chip: float, api_latency: float) -> str:
    if T_chip < 75 and api_latency <= 200:
        return "local"
    if api_latency > 200:
        return "local"
    return "api"


class DispatchAgent:
    def step(
        self,
        T_chip: float,
        soc_pct: float,
        P_pv: float,
        P_wwtp: float,
        P_grid: float,
        api_latency: float,
        load_factor: float,
        P_bess_chg: float = 0.0,
        P_bess_dis: float = 0.0,
        balance_error: float = 0.0,
    ) -> dict:
        bess_kwh = soc_pct / 100.0 * SOC_MAX_KWH
        if P_bess_dis > 0:
            bess_action = "discharging"
            bess_power = P_bess_dis
        elif P_bess_chg > 0:
            bess_action = "charging"
            bess_power = P_bess_chg
        else:
            bess_action = "idle"
            bess_power = 0.0

        local_pct_val = 100 if api_latency > 200 else (90 if api_latency > 100 else 50)
        state = {
            "T_chip": T_chip,
            "P_wwtp": P_wwtp,
            "bess_soc": soc_pct,
            "bess_kwh": bess_kwh,
            "api_latency": api_latency,
            "balance_error": balance_error,
            "P_pv": P_pv,
            "P_grid": P_grid,
            "load_factor": load_factor,
            "bess_action": bess_action,
            "bess_power": bess_power,
            "P_aeration": max(0, P_wwtp - 750),
            "local_pct": local_pct_val,
        }

        routing = _route_decision(T_chip, api_latency)
        anomalies = _detect_anomalies(state)

        # Build reasoning string (always non-empty).
        parts = [f"T_chip={T_chip:.1f}°C", f"SOC={soc_pct:.0f}%", f"API={api_latency:.0f}ms"]
        if T_chip > 78:
            throttle = min(100, max(0, (T_chip - 78) / (85 - 78) * 100))
            parts.append(f"throttle {throttle:.0f}%")
        else:
            throttle = 0.0
        parts.append(f"route={routing}")
        reasoning = " | ".join(parts)

        rca = None
        if anomalies:
            descriptions = []
            for a in anomalies:
                tpl = ANOMALY_TEMPLATES.get(a, a)
                try:
                    descriptions.append(tpl.format(**state))
                except KeyError:
                    descriptions.append(a)
            anomaly_desc = " ".join(descriptions)
            prompt = WWTP_DC_RCA_PROMPT.format(
                anomaly_description=anomaly_desc, **state
            )
            rca = _call_llm(prompt)

        alert_level = 0
        if anomalies:
            alert_level = 1
        if "thermal" in anomalies and T_chip > 82:
            alert_level = 2
        if "energy_violation" in anomalies:
            alert_level = 2

        return {
            "routing": routing,
            "throttle_pct": throttle,
            "alert_level": alert_level,
            "reasoning": reasoning,
            "rca": rca,
        }


if __name__ == "__main__":
    agent = DispatchAgent()

    print("=== Normal operation ===")
    r = agent.step(T_chip=65, soc_pct=50, P_pv=3000, P_wwtp=2500, P_grid=1000,
                   api_latency=40, load_factor=0.7)
    print(f"  routing={r['routing']}  alert={r['alert_level']}  reasoning={r['reasoning']}")
    assert r["reasoning"], "reasoning must be non-empty"

    print("\n=== Thermal stress ===")
    r = agent.step(T_chip=82, soc_pct=20, P_pv=1000, P_wwtp=3100, P_grid=3500,
                   api_latency=50, load_factor=0.95)
    print(f"  routing={r['routing']}  alert={r['alert_level']}  reasoning={r['reasoning']}")
    print(f"  rca={r['rca'][:80]}...")
    assert r["rca"] is not None, "RCA should fire on thermal anomaly"
    assert r["reasoning"], "reasoning must be non-empty"

    print("\n=== Network congestion ===")
    r = agent.step(T_chip=68, soc_pct=40, P_pv=2000, P_wwtp=2200, P_grid=2000,
                   api_latency=350, load_factor=0.8)
    print(f"  routing={r['routing']}  alert={r['alert_level']}  reasoning={r['reasoning']}")
    assert r["rca"] is not None
    assert r["reasoning"]

    print("\nStep 8 verification: PASS")
