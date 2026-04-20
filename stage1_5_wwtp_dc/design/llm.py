"""NVIDIA NIM chat client + tool-calling loop for Blog 2.

Exposes three things:

* ``make_client(api_key)`` — lazy OpenAI-compatible client wired to
  ``integrate.api.nvidia.com``.
* ``SYSTEM_PROMPT`` — the Blog 2 assistant's role definition.
* ``run_tool_loop(client, messages, max_steps=6)`` — the agent loop that
  alternates between LLM responses and tool executions until the LLM
  returns a final text answer (or the loop hits the step cap).

The loop is intentionally small and self-contained. No LangChain, no
OpenAI-client SDK wrapping. A reader of Blog 2 can follow every line.

Registers all tools from ``design.pv_tools`` and ``design.rag``, plus two
adapters for ``design.sizing.size_site`` and
``design.archetypes.ARCHETYPES`` so the LLM can ground its reasoning in the
parametric MGD presets when the conversation calls for it.
"""
from __future__ import annotations

import json
import os
from typing import Any, Callable, Dict, List, Tuple

from .pv_tools import TOOL_SCHEMAS as _PV_SCHEMAS, TOOL_DISPATCH as _PV_DISPATCH
from .rag import TOOL_SCHEMAS as _RAG_SCHEMAS, TOOL_DISPATCH as _RAG_DISPATCH


# ---------------------------------------------------------------------------
# Expose size_site / ARCHETYPES as tools too
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
# System prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """\
You are a senior Solutions Architect helping a client scope a behind-the-meter
AI inference site colocated with a municipal wastewater treatment plant.
Your job is to walk the client through the sizing decisions — PV technology,
hardware choice, BESS duration, site regulations, CAPEX — and produce a
specific, numbered design proposal grounded in real engineering references.

## Ground rules

1. ALWAYS call the `retrieve` tool before answering any question about
   hardware, PV, BESS, regulations, or CAPEX. The retrieved wiki entries
   are your source of truth. If a question has no wiki support, say so
   rather than inventing numbers.

2. For sizing math, call the appropriate numeric tool:
   • `design_pv_array` for module count + string config
   • `calc_annual_yield` for MWh/yr and capacity factor
   • `compare_pv_technologies` when the user is choosing tracker type
   • `size_site` + `list_archetypes` for standard 30/40/50/60 MGD bundles

3. Every numeric claim in your final text answer must be traceable to
   either (a) a tool output the client has just seen, or (b) a wiki
   excerpt you retrieved this turn. If you don't have either, your
   response should say: "I don't have a grounded number for that yet —
   want me to pull it from a source?"

4. Be opinionated. The client is a PE-licensed industrial engineer and
   hates hedging. When a tradeoff has a clearly better default (e.g.
   single-axis tracker vs fixed tilt at 30°N), say so and cite the reason.

5. Keep responses short — one screenful at a time. Break long designs
   into numbered decision steps so the client can approve or adjust each.

## Conversation shape

Turn 1–2: establish site location, plant size, available acres.
Turn 3–5: walk through PV tech → hardware → BESS decisions, calling tools.
Turn 6+: summarize a numbered site plan with CAPEX/revenue estimates.

When you present numbers, always show which tool (or wiki file) produced
them. Example: "PV nameplate 6,840 kWp (design_pv_array)" or "Lazard 2024
CAPEX $1.05/W (capex/pv_lazard_lcoe_2024.md)".
"""


# ---------------------------------------------------------------------------
# Client factory (lazy OpenAI-compatible wrapper)
# ---------------------------------------------------------------------------
def make_client(api_key: str | None = None, model: str | None = None):
    """Return an OpenAI-compatible client pointed at NVIDIA NIM, plus the
    chosen model name. Raises RuntimeError if openai package is not
    installed (the Streamlit app handles that by falling back to mock mode).
    """
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "openai package not installed; run `pip install openai>=1.30`"
        ) from exc

    # Accept either NVIDIA_API_KEY (stage1 convention, already in user's .env)
    # or NVIDIA_NIM_API_KEY (newer convention some docs use). First match wins.
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
# Tool-calling loop
# ---------------------------------------------------------------------------
def run_tool_loop(
    client,
    model: str,
    messages: List[Dict[str, Any]],
    max_steps: int = 6,
    tools: List[Dict[str, Any]] | None = None,
    dispatch: Dict[str, Callable[..., Any]] | None = None,
) -> Tuple[List[Dict[str, Any]], str, List[Dict[str, Any]]]:
    """Run the tool-calling loop until the LLM produces a final text answer.

    Parameters
    ----------
    client, model : output of ``make_client``.
    messages : chat history; the caller is responsible for prepending the
        system prompt. This function appends assistant + tool messages.
    max_steps : cap on assistant-tool round trips per user turn.
    tools, dispatch : override tool registry; default is ``ALL_TOOL_*``.

    Returns
    -------
    (messages, final_text, tool_calls_log)
        The updated message history, the LLM's final text content, and a
        list of ``{tool, args, result}`` dicts for UI display / auditing.
    """
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

        # Serialize assistant message for history. OpenAI SDK returns an object;
        # convert to the dict shape the next API call expects.
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

        # No tool calls → we have a final text answer.
        if not msg.tool_calls:
            return messages, msg.content or "", tool_calls_log

        # Otherwise, execute each tool, append tool result messages, loop.
        for tc in msg.tool_calls:
            name = tc.function.name
            raw_args = tc.function.arguments or "{}"
            try:
                args = json.loads(raw_args)
            except json.JSONDecodeError:
                args = {}

            fn = dispatch.get(name)
            if fn is None:
                result: Any = {"error": f"unknown tool: {name}"}
            else:
                try:
                    result = fn(**args)
                except Exception as e:  # noqa: BLE001 — surface to the LLM
                    result = {"error": f"{type(e).__name__}: {e}"}

            tool_calls_log.append({"tool": name, "args": args, "result": result})

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": name,
                    "content": json.dumps(result, default=_json_default),
                }
            )

    # Step cap hit; append a synthetic assistant close-out so UI is consistent.
    fallback = (
        "I used my allotted tool calls for this turn. Here's what I have so far. "
        "Ask me to continue and I'll pick up where I left off."
    )
    messages.append({"role": "assistant", "content": fallback})
    return messages, fallback, tool_calls_log


def _json_default(o: Any) -> Any:
    """Serialize numpy / dataclass-ish things the tool returns may contain."""
    import numpy as np
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)
