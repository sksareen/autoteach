# Autoresolve

A simple app that reinforces your resolve, and keeps getting better at it on its own.

You set one commitment ("run 3 mornings a week", "no takeout until the card is paid off"). When your resolve wobbles, you open the app and talk it through with a coach. Behind the scenes, an autoresearch loop (inspired by [Karpathy's autoresearch](https://github.com/karpathy/autoresearch)) keeps rewriting the coach, testing it against simulated people in hard moments, and keeping only the changes that help more of them hold the line.

## Two halves

```
┌───────────────────────────┐        ┌──────────────────────────────────┐
│  app.py  (the product)    │        │  Claude Code (the researcher)    │
│  - set one commitment     │        │  - reads program.md              │
│  - check in when wobbling │        │  - edits coach.py                │
│  - logs kept / slipped    │        │  - runs evaluate.py              │
└────────────┬──────────────┘        │  - keeps wins, reverts losses    │
             │ loads                 └───────────────┬──────────────────┘
             ▼                                       │ edits
      ┌──────────────┐ ◄─────────────────────────────┘
      │  coach.py    │  the coach's system prompt
      └──────────────┘ ◄──── evaluate.py → prepare.py (fixed test)
```

## Files

| File | Role | Modifiable by the loop? |
|---|---|---|
| `app.py` | The CLI app real people use | No |
| `coach.py` | The coach's system prompt | **Yes, the only file** |
| `prepare.py` | Fixed personas, wobble moments, simulation, integrity judge, score | No |
| `evaluate.py` | Thin runner | No |
| `llm.py` | Shared OpenRouter helper (no dependencies) | No |
| `program.md` | Instructions for the autonomous researcher | No |

## The test

Four simulated people, each with one resolution, each hit with the same four kinds of wobble moment:

| Person | Commitment | Moments |
|---|---|---|
| Dana, 41 | Run 3 mornings a week | excuse · temptation · after a slip · social pressure |
| Theo, 29 | Write 300 words every weekday | same four |
| Rosa, 35 | No takeout or impulse buys until debt is paid | same four |
| Sam, 22 | Phone out of the bedroom after 11pm | same four |

The simulated person defaults to giving in, and generic pep talk or guilt makes that more likely. They end each moment with `KEPT` or `SLIPPED`. A judge then checks that the coach played fair: no shaming, no invented facts, no manipulation. A moment only counts if the person held **and** the coach passed integrity.

```
score = hold_rate - 0.001 * avg_coach_words
```

Higher is better. It rewards helping more people hold, in fewer words.

## Running it

Requires Python 3.11+, [uv](https://docs.astral.sh/uv/), and an OpenRouter key in `OPENROUTER_API_KEY`. All model calls go through OpenRouter. The model defaults to `anthropic/claude-opus-5.5`; override with any OpenRouter model ID via `RESOLVE_MODEL`.

**Use the app:**
```bash
uv run app.py           # first run asks for your commitment, then checks in
uv run app.py --reset   # start a new commitment
```
State lives in `~/.resolve.json`.

**Score the current coach once:**
```bash
uv run evaluate.py
```
Roughly 100–130 API calls per run.

**Start the self-improvement loop:**
```bash
claude
> Read program.md and let's kick off a new experiment
```

Claude Code creates an `autoresearch/<tag>` branch, records a baseline, then loops: edit `coach.py` → commit → evaluate → keep or revert → repeat, logging every run to `results.tsv`.
