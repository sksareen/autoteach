"""
Resolve: the app. Set one commitment, then open it whenever your resolve wobbles.
Usage: uv run app.py           (check in)
       uv run app.py --reset   (set a new commitment)
"""

import json
import sys
from datetime import date
from pathlib import Path

from coach import SYSTEM_PROMPT
from llm import call

STATE_FILE = Path.home() / ".resolve.json"


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return None


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))


def setup():
    print("What's the one commitment you want to keep?")
    resolution = input("> ").strip()
    print("Why does it matter to you? (in your own words)")
    why = input("> ").strip()
    state = {"resolution": resolution, "why": why, "started": date.today().isoformat(), "log": []}
    save_state(state)
    print(f"\nLocked in: {resolution}\nOpen this app whenever it gets hard.\n")
    return state


def check_in(state):
    past = "\n".join(f"- {e['date']}: {e['outcome']}" for e in state["log"][-10:]) or "- none yet"
    system = (
        SYSTEM_PROMPT
        + f"\n\n## This person\nCommitment: {state['resolution']}\n"
        + f"Their reason: {state['why']}\nPast check-ins:\n{past}"
    )
    print(f"Commitment: {state['resolution']}")
    print("What's going on right now? (empty line to finish)\n")

    messages = []
    while True:
        text = input("you> ").strip()
        if not text:
            break
        messages.append({"role": "user", "content": text})
        reply = call(system, messages)
        messages.append({"role": "assistant", "content": reply})
        print(f"\ncoach> {reply}\n")

    if messages:
        answer = input("Did you keep it this time? [y/n] ").strip().lower()
        outcome = "kept it" if answer.startswith("y") else "slipped"
        state["log"].append({"date": date.today().isoformat(), "outcome": outcome})
        save_state(state)
        kept = sum(e["outcome"] == "kept it" for e in state["log"])
        print(f"Logged. You've held {kept} of {len(state['log'])} hard moments.")


if __name__ == "__main__":
    state = None if "--reset" in sys.argv else load_state()
    check_in(state or setup())
