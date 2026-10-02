"""
Shared Claude API helper used by both the app and the evaluation harness.
"""

import os

import anthropic

MODEL = os.environ.get("RESOLVE_MODEL", "claude-opus-5-5")

_client = None
stats = {"api_calls": 0, "input_tokens": 0, "output_tokens": 0}


def call(system, messages, max_tokens=4000, effort="low"):
    """One Messages API call. Returns the response text ("" on refusal)."""
    global _client
    if _client is None:
        _client = anthropic.Anthropic()

    response = _client.beta.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=messages,
        output_config={"effort": effort},
        # On a safety decline, re-run on a fallback model chosen by the server.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )

    stats["api_calls"] += 1
    stats["input_tokens"] += response.usage.input_tokens
    stats["output_tokens"] += response.usage.output_tokens

    if response.stop_reason == "refusal":
        return ""
    return "".join(b.text for b in response.content if b.type == "text").strip()


def reset_stats():
    for k in stats:
        stats[k] = 0
