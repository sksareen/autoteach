"""
Shared model helper used by both the app and the evaluation harness.
All calls go through OpenRouter, authenticated with OPENROUTER_API_KEY.
"""

import json
import os
import time
import urllib.error
import urllib.request

URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = os.environ.get("RESOLVE_MODEL", "anthropic/claude-opus-5.5")

stats = {"api_calls": 0, "input_tokens": 0, "output_tokens": 0}


def call(system, messages, max_tokens=4000, effort="low", retries=3):
    """One chat completion. Returns the response text."""
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise SystemExit("Set OPENROUTER_API_KEY (https://openrouter.ai/keys).")

    body = json.dumps({
        "model": MODEL,
        "max_tokens": max_tokens,
        "messages": [{"role": "system", "content": system}, *messages],
        "reasoning": {"effort": effort},
    }).encode()
    request = urllib.request.Request(URL, data=body, headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "X-Title": "autoresolve",
    })

    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                data = json.load(response)
            break
        except urllib.error.HTTPError as e:
            # Retry rate limits and server errors; anything else is a real bug.
            if attempt == retries or (e.code != 429 and e.code < 500):
                raise
        except urllib.error.URLError:
            if attempt == retries:
                raise
        time.sleep(2 ** (attempt + 1))

    stats["api_calls"] += 1
    usage = data.get("usage") or {}
    stats["input_tokens"] += usage.get("prompt_tokens", 0)
    stats["output_tokens"] += usage.get("completion_tokens", 0)
    return (data["choices"][0]["message"].get("content") or "").strip()


def reset_stats():
    for k in stats:
        stats[k] = 0
