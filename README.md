# Autoresearch: AI Literacy Tutor

An autoresearch project that autonomously optimizes an AI teaching agent. Inspired by [Karpathy's autoresearch](https://github.com/karpathy/autoresearch) — but instead of training neural nets on a GPU, we're iterating on a teaching strategy via API calls.

## What This Does

An AI agent (Claude Code) autonomously modifies a tutor's teaching strategy (`tutor.py`), runs it against 5 simulated learners, measures how well they learned, and keeps or discards changes — looping forever until you stop it.

**The research question:** What's the optimal way to teach anyone AI literacy?

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Claude Code (the autonomous researcher)        │
│  - Reads program.md for instructions            │
│  - Modifies tutor.py (teaching strategy)        │
│  - Runs evaluate.py, reads results              │
│  - Keeps improvements, discards regressions     │
│  - Loops forever until you stop it              │
└──────────────────┬──────────────────────────────┘
                   │ runs
                   ▼
┌─────────────────────────────────────────────────┐
│  evaluate.py → prepare.py                       │
│  For each of 5 personas:                        │
│    1. Tutor ↔ Learner conversation (API calls)  │
│    2. Learner takes 5 assessment tasks           │
│    3. Judge grades each task PASS/FAIL           │
│  Outputs: score, pass_rate, avg_turns            │
└─────────────────────────────────────────────────┘
```

## Files

| File | Role | Modifiable? |
|---|---|---|
| `program.md` | Instructions for the autonomous researcher (Claude Code) | No |
| `prepare.py` | Fixed infrastructure: personas, tasks, evaluation harness | No |
| `tutor.py` | The teaching agent's brain: system prompt, tools, strategy | **Yes — this is the only file the agent modifies** |
| `evaluate.py` | Thin runner script (7 lines) | No |
| `results.tsv` | Experiment log (created during runs, not committed) | Append-only |

## The 5 Learner Personas

| ID | Name | Who | Resistance |
|---|---|---|---|
| `mom` | Priya | 58yo mother, iPhone/Google user, loves cooking | "Why would I need this when Google works fine?" |
| `barber` | Marcus | 34yo barber in PA, runs his own shop, paper calendar | "I don't have time to learn new tech." |
| `creative` | Maya | 28yo illustrator, tried ChatGPT, found it generic | "It just gives bland generic stuff." |
| `student` | Jake | 20yo college sophomore, copy-pastes ChatGPT essays | "I already use ChatGPT all the time." |
| `retiree` | Bob | 65yo retired accountant, loves spreadsheets | "I don't want to look foolish." |

## The 5 Assessment Tasks (Universal Skills)

Each persona gets a persona-specific scenario, but the underlying skill is the same:

| # | Skill | What It Tests |
|---|---|---|
| 1 | **Prompting** | Can they use AI to solve a real problem? |
| 2 | **Debugging** | When AI gives bad output, can they diagnose and fix it? |
| 3 | **Critical Thinking** | Do they know AI can be wrong, and what to do about it? |
| 4 | **Persistence** | Can they set up AI to remember their context? |
| 5 | **Building** | Can they use AI to create a reusable tool? |

## The Metric

```
score = pass_rate - 0.005 * avg_turns
```

- `pass_rate`: tasks passed / 25 (5 personas × 5 tasks), range 0.0–1.0
- `avg_turns`: average conversation length across personas
- Higher score is better
- Rewards: more tasks passed, fewer turns needed (efficient teaching)

## How to Run

### Prerequisites
- Python 3.11+
- `uv` installed
- OpenRouter API key with credits

### Single Evaluation Run
```bash
export OPENROUTER_API_KEY=sk-or-v1-...
cd ~/coding/autoresearch-teach
uv run evaluate.py
```

**What to expect:**
- Takes ~15-25 minutes (5 personas × ~3-5 min each)
- ~150-200 API calls per run
- ~$1-3 per run depending on conversation length
- Prints progress per persona, then final score

### Autonomous Research Loop (the real thing)
```bash
export OPENROUTER_API_KEY=sk-or-v1-...
cd ~/coding/autoresearch-teach
claude
```

Then say:
```
Read program.md and let's kick off a new experiment
```

Claude Code will:
1. Read all files for context
2. Create a git branch `autoresearch/<tag>`
3. Run the baseline evaluation
4. Start the loop: modify tutor.py → commit → run → keep/discard → repeat
5. **Never stop** until you interrupt it (Ctrl+C)

**What to expect overnight:**
- ~3-4 experiments per hour (each run is ~15-25 min)
- ~25-30 experiments in 8 hours
- ~$30-80 in API costs overnight
- Results logged in `results.tsv`
- Git history shows every experiment (kept experiments advance the branch)

## Output Example

```
============================================================
Persona: Priya (mom)
============================================================
  Teaching... done (14 turns)
  Assessing... done (3/5 passed)
    get_useful           PASS
    fix_broken           PASS
    catch_bs             FAIL
    make_persistent      PASS
    build_thing          FAIL

[... repeats for all 5 personas ...]

============================================================
Per-persona breakdown:
  Priya        3/5 passed, 14 turns  [✓ ✓ ✗ ✓ ✗]
  Marcus       3/5 passed, 12 turns  [✓ ✓ ✗ ✓ ✗]
  Maya         4/5 passed, 10 turns  [✓ ✓ ✓ ✓ ✗]
  Jake         3/5 passed,  8 turns  [✓ ✗ ✓ ✓ ✗]
  Bob          2/5 passed, 18 turns  [✓ ✓ ✗ ✗ ✗]

---
score:           0.437600
pass_rate:       0.6000
tasks_passed:    15/25
avg_turns:       12.4
total_api_calls: 172
cost_estimate:   $2.14
```

## What the Researcher Iterates On

The agent modifies `tutor.py`, which contains:
- **System prompt**: the tutor's personality, teaching philosophy, pacing rules
- **Teaching sequence**: what order to present concepts
- **Tool definitions**: what interactive tools the tutor can use (playground, sandbox, failure demos, comparisons)
- **Decision rules**: when to intervene vs. let them struggle, when to move on

Example experiments the agent might try:
- Reorder teaching sequence (build something first?)
- Remove a tool (is `show_comparison` even needed?)
- Change the opening strategy (ask about their life vs. jump into a demo)
- Shorten the system prompt (can you teach the same with less instruction?)
- Add a new tool (e.g., `show_before_after` for prompt improvement)
- Change pacing rules (signal [ASSESS] earlier)

## Background & Motivation

This project came from a conversation about Karpathy's autoresearch and what research would make sense given Savar's projects (Vahana, HOW TO AI, Simply Human). The core thesis:

> The problem with AI education isn't explaining capabilities — it's manufacturing the "unlock moment." What triggers it? How fast can you get there? What kills it?

The 5 assessment tasks represent universal AI literacy skills that work for anyone — a mother, a barber, a creative professional, a student, a retiree. The teaching strategy that scores highest across all of them is, by definition, universally effective.

Results from this research feed directly into:
- **HOW TO AI** (`~/coding/how-to-ai/`) — the teaching framework
- **Simply Human** (simpli.substack.com) — publishable findings
- **Vahana** (`~/coding/vahana/`) — the interactive teaching environment

## API Configuration

Uses OpenRouter with the OpenAI-compatible SDK:
- Model: `anthropic/claude-sonnet-4-6`
- Base URL: `https://openrouter.ai/api/v1`
- Auth: `OPENROUTER_API_KEY` environment variable

## First Test Run Result (Mar 9, 2026)

Single persona test (Marcus the barber):
- 3/5 passed (prompting ✓, debugging ✓, BS detection ✗, persistence ✓, building ✗)
- 12 turns, 35 API calls
- Pipeline confirmed working end-to-end
