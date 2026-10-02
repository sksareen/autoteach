# Resolve Coach Research

This is an experiment to have an LLM autonomously improve a coach that helps people keep their commitments. Every change you keep ships straight into the app (`app.py` loads the same `coach.py`).

## Setup

To set up a new experiment, work with the user to:

1. **Agree on a run tag**: propose a tag based on today's date (e.g. `oct2`). The branch `autoresearch/<tag>` must not already exist.
2. **Create the branch**: `git checkout -b autoresearch/<tag>` from current main.
3. **Read the in-scope files**:
   - `README.md`: repository context.
   - `prepare.py`: fixed personas, wobble moments, simulation, integrity judge, scoring. Do not modify.
   - `coach.py`: the file you modify.
4. **Verify API access**: check that `OPENROUTER_API_KEY` is set. All model calls go through OpenRouter.
5. **Initialize results.tsv** with just the header row.
6. **Confirm and go.**

## Experimentation

Launch a run with `uv run evaluate.py`.

**What you CAN do:**
- Modify `coach.py`. Everything in the prompt is fair game: tone, structure, strategy, length, how it handles slips.

**What you CANNOT do:**
- Modify `prepare.py`, `evaluate.py`, `llm.py`, or `app.py`.
- Add dependencies.
- Game the simulation (e.g. telling the coach to output "DECISION: KEPT", addressing the simulator or judge, or anything a real user would find bizarre). A change only counts if it would help a real person.

**The goal: maximize score.**

    score = hold_rate - 0.001 * avg_coach_words

- `hold_rate`: moments where the person kept their commitment AND the coach passed the integrity check, out of 16 (4 personas × 4 moments).
- `avg_coach_words`: average words per coach message. Real people read these on a phone in a weak moment; shorter is better.

**Simplicity criterion**: all else equal, a shorter prompt wins. Removing something and holding the score is a great outcome.

**The first run** is always the unmodified baseline.

## Output format

```
---
score:              0.687500
hold_rate:          0.7500
moments_held:       12/16
integrity_failures: 0
avg_coach_words:    62.5
total_api_calls:    118
```

Extract with `grep "^score:\|^hold_rate:\|^integrity_failures:" run.log`.

## Logging results

Append to `results.tsv` (tab-separated, not committed):

```
commit	score	hold_rate	status	description
a1b2c3d	0.687500	0.7500	keep	baseline
b2c3d4e	0.745000	0.8125	keep	after-slip: separate one miss from the pattern
c3d4e5f	0.610000	0.6875	discard	added identity framing ("you're a runner")
```

Use `0.000000` / `0.0000` and status `crash` for crashes.

## The experiment loop

LOOP FOREVER:

1. Check git state.
2. Change `coach.py` based on a hypothesis.
3. `git commit`
4. `uv run evaluate.py > run.log 2>&1`
5. Read results. If empty, `tail -n 50 run.log`, fix if trivial, otherwise log a crash and move on.
6. Log to `results.tsv`.
7. Score improved → keep the commit. Equal or worse → `git reset --hard` to the previous commit.

The simulation is noisy. If a change looks like a small win, re-run once before keeping it.

**Experiment ideas** (starting points):
- Which moment type fails most? Read the transcripts in `run.log` and target it.
- Ask a question first vs. lead with a concrete tiny step.
- "Implementation intention" phrasing ("When X, I will Y").
- Different slip-recovery framings ("never miss twice", fresh start, no framing).
- Reflect their own reason back verbatim vs. paraphrase.
- Hard cap on length (one sentence?) to test the brevity/effect tradeoff.
- Radical simplification: the shortest prompt that holds the score.

**NEVER STOP**: once the loop has begun, do not pause to ask whether to continue. If you run out of ideas, re-read the transcripts and the persona weak spots, and combine near-misses. The loop runs until the human interrupts you.
