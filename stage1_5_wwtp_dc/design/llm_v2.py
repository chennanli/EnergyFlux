"""NVIDIA NIM chat client + tool-calling loop for Blog 2 — vault edition.

Successor to ``design.llm``. Same shape, two differences:

1. **Retrieves from the EnergyFlux knowledge vault**
   (``design.rag_v2.VaultRetriever``) instead of the legacy
   ``design_wiki/``.

2. **System prompt enforces authority discipline.** The LLM is told
   to cite Authoritative + Reviewed pages as primary; Candidate /
   Legacy hits must be labeled "pending review" if used at all.

The tool-calling loop itself is unchanged — same OpenAI-compatible
client, same iterative tool-then-respond shape.
"""
from __future__ import annotations

import json
import os
from typing import Any, Callable, Dict, List, Tuple

from .pv_tools import TOOL_SCHEMAS as _PV_SCHEMAS, TOOL_DISPATCH as _PV_DISPATCH
from .rag_v2 import TOOL_SCHEMAS as _RAG_SCHEMAS, TOOL_DISPATCH as _RAG_DISPATCH


# ---------------------------------------------------------------------------
# Sizing tools (same as legacy llm.py)
# ---------------------------------------------------------------------------
def _size_site_tool(archetype_name: str) -> Dict[str, Any]:
    from .sizing import size_site
    return size_site(archetype_name)


def _list_archetypes() -> Dict[str, Any]:
    from .archetypes import ARCHETYPES, ARCHETYPE_LABELS
    return {
        name: {"label": ARCHETYPE_LABELS[name], **ARCHETYPES[name]}
        for name in ARCHETYPES
    }


_SIZING_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "size_site",
            "description": (
                "Return the full sizing report (PV + BESS + DC + revenue) for "
                "one of the four registered WWTP archetypes. Use when the user "
                "specifies a plant size bucket like '30 MGD' or '60 MGD'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "archetype_name": {
                        "type": "string",
                        "enum": ["wwtp_30mgd", "wwtp_40mgd", "wwtp_50mgd", "wwtp_60mgd"],
                    },
                },
                "required": ["archetype_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_archetypes",
            "description": "List the four registered WWTP archetype presets and their raw input constants.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]

_SIZING_DISPATCH: Dict[str, Callable[..., Any]] = {
    "size_site": _size_site_tool,
    "list_archetypes": lambda: _list_archetypes(),
}


# ---------------------------------------------------------------------------
# All tools rolled up
# ---------------------------------------------------------------------------
ALL_TOOL_SCHEMAS: List[Dict[str, Any]] = (
    _PV_SCHEMAS + _RAG_SCHEMAS + _SIZING_SCHEMAS
)
ALL_TOOL_DISPATCH: Dict[str, Callable[..., Any]] = {
    **_PV_DISPATCH, **_RAG_DISPATCH, **_SIZING_DISPATCH
}


# ---------------------------------------------------------------------------
# System prompt (authority-aware)
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """\
You are a senior Solutions Architect helping a client scope a behind-the-meter
AI inference site colocated with a municipal wastewater treatment plant.
Your knowledge source is the EnergyFlux Knowledge Vault, accessed via the
`retrieve` tool. Your job is to walk the client through the sizing decisions
— PV technology, hardware choice, BESS duration, site regulations, CAPEX —
and produce a specific, numbered design proposal grounded in real engineering
references.

## Vault authority discipline

Every retrieved hit carries an `authority` field with one of four values:

* **authoritative** — external primary source (NREL ATB, NVIDIA datasheet,
  NERC standard, EPA dataset, peer-reviewed paper). Cite as fact.
* **reviewed** — human-approved synthesis. A senior engineer has read the
  page, checked the citations, and signed off. Cite as fact.
* **candidate** — LLM-drafted or unreviewed synthesis. May be used as a
  starting point, but you MUST label it "pending review" in your reply.
* **legacy** — imported from earlier work, not yet re-validated. Same
  treatment as candidate: label "pending review" if cited.

Rules:

1. ALWAYS call `retrieve` before answering any domain question. The
   retrieved hits are your source of truth.

2. When composing your answer, prefer **authoritative** and **reviewed**
   hits as primary citations. If only **candidate** or **legacy** hits
   are available, you MAY still answer, but you MUST prefix that part of
   your answer with: "(pending review — vault page is candidate / legacy
   level and has not been signed off by a senior engineer)".

3. Every numeric claim must be traceable to either (a) a tool output the
   client has just seen, or (b) a vault hit you retrieved this turn.
   Cite the vault page by title and authority level.

   Good: "Per-rack draw is ~125 kW (vault: *NVIDIA Blackwell GB200 NVL72*,
   candidate level — pending review)."

   Bad: "Per-rack draw is about 125 kW." (No citation, no authority.)

4. For sizing math, call the appropriate numeric tool:
   • `design_pv_array` for module count + string config
   • `calc_annual_yield` for MWh/yr and capacity factor
   • `compare_pv_technologies` when the user is choosing tracker type
   • `size_site` + `list_archetypes` for standard 30/40/50/60 MGD bundles

5. Be opinionated where the vault supports a clear default. The client
   is a PE-licensed industrial engineer and dislikes hedging. If the
   vault says single-axis bifacial is the default at 30°N, say so.

6. Keep responses short — one screenful. Numbered decision steps when
   the conversation is converging on a design.

## Conversation shape

Turn 1–2: establish site location, plant size, available acres.
Turn 3–5: walk PV → hardware → BESS → grid, calling tools.
Turn 6+: numbered site plan with CAPEX/revenue estimates and a list of
the vault pages cited (with their authority levels) at the end.
"""


# ---------------------------------------------------------------------------
# Client factory (identical to legacy llm.py)
# ---------------------------------------------------------------------------
def make_client(api_key: str | None = None, model: str | None = None):
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "openai package not installed; run `pip install openai>=1.30`"
        ) from exc

    key = api_key or os.getenv("NVIDIA_API_KEY") or os.getenv("NVIDIA_NIM_API_KEY")
    if not key:
        raise RuntimeError(
            "NVIDIA_API_KEY missing from environment. Get a free key at "
            "build.nvidia.com and add `NVIDIA_API_KEY=nvapi-...` to your "
            ".env file, or paste it into the Streamlit sidebar."
        )

    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=key,
    )
    return client, model or "meta/llama-3.1-70b-instruct"


# ---------------------------------------------------------------------------
# Tool-calling loop (identical to legacy llm.py)
# ---------------------------------------------------------------------------
def run_tool_loop(
    client,
    model: str,
    messages: List[Dict[str, Any]],
    max_steps: int = 6,
    tools: List[Dict[str, Any]] | None = None,
    dispatch: Dict[str, Callable[..., Any]] | None = None,
) -> Tuple[List[Dict[str, Any]], str, List[Dict[str, Any]]]:
    tools = tools or ALL_TOOL_SCHEMAS
    dispatch = dispatch or ALL_TOOL_DISPATCH
    tool_calls_log: List[Dict[str, Any]] = []

    for step in range(max_steps):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.25,
            max_tokens=1200,
        )
        msg = response.choices[0].message

        assistant_msg: Dict[str, Any] = {
            "role": "assistant",
            "content": msg.content,
        }
        if msg.tool_calls:
            assistant_msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in msg.tool_calls
            ]
        messages.append(assistant_msg)

        if not msg.tool_calls:
            return messages, msg.content or "", tool_calls_log

        for tc in msg.tool_calls:
            name = tc.function.name
            raw_args = tc.function.arguments or "{}"
            try:
                args = json.loads(raw_args)
            except json.JSONDecodeError:
                args = {}
            try:
                result = dispatch[name](**args) if name in dispatch else {
                    "error": f"unknown tool: {name}"
                }
            except Exception as exc:  # noqa: BLE001
                result = {"error": f"{type(exc).__name__}: {exc}"}
            tool_calls_log.append({"tool": name, "args": args, "result": result})
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "name": name,
                "content": json.dumps(result, default=str),
            })

    # Loop exhausted — fall back to a final synthesis pass.
    final = client.chat.completions.create(
        model=model,
        messages=messages + [{
            "role": "user",
            "content": "Summarize what we have so far in your final answer.",
        }],
        temperature=0.25,
        max_tokens=1200,
    )
    final_text = final.choices[0].message.content or ""
    messages.append({"role": "assistant", "content": final_text})
    return messages, final_text, tool_calls_log
