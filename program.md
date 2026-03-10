# AI Literacy Tutor Research

This is an experiment to have an LLM autonomously optimize an AI teaching agent.

## Setup

To set up a new experiment, work with the user to:

1. **Agree on a run tag**: propose a tag based on today's date (e.g. `mar9`). The branch `autoresearch/<tag>` must not already exist — this is a fresh run.
2. **Create the branch**: `git checkout -b autoresearch/<tag>` from current main.
3. **Read the in-scope files**: The repo is small. Read these files for full context:
   - `README.md` — repository context.
   - `prepare.py` — fixed infrastructure: personas, assessment tasks, evaluation. Do not modify.
   - `tutor.py` — the file you modify. Teaching strategy, system prompt, tool definitions.
4. **Verify API access**: Check that `ANTHROPIC_API_KEY` is set in the environment.
5. **Initialize results.tsv**: Create `results.tsv` with just the header row. The baseline will be recorded after the first run.
6. **Confirm and go**: Confirm setup looks good.

Once you get confirmation, kick off the experimentation.

## Experimentation

Each experiment runs via API calls. You launch it simply as: `uv run evaluate.py`.

**What you CAN do:**
- Modify `tutor.py` — this is the only file you edit. Everything is fair game: system prompt, teaching strategy, tool definitions, tool parameters, sequencing rules. You can add tools, remove tools, rewrite the entire pedagogy.

**What you CANNOT do:**
- Modify `prepare.py`. It is read-only. It contains the fixed personas, assessment tasks, rubrics, evaluation, and scoring.
- Modify `evaluate.py`. It is the thin runner script.
- Install new packages or add dependencies.
- Modify the assessment rubrics or personas.

**The goal is simple: maximize score.** The score formula is:

    score = pass_rate - 0.005 * avg_turns

Higher is better. You want all 5 personas to pass all 5 tasks in as few conversation turns as possible. `pass_rate` ranges from 0.0 to 1.0 (25 total pass/fail grades: 5 personas × 5 tasks). `avg_turns` is the average conversation length across personas.

**Simplicity criterion**: All else being equal, simpler is better. A small improvement that adds ugly complexity to the tutor prompt is not worth it. Conversely, removing something and getting equal or better results is a great outcome — that's a simplification win. When evaluating whether to keep a change, weigh the complexity cost against the improvement magnitude.

**The first run**: Your very first run should always be to establish the baseline, so you will run the evaluation as is.

## Output format

Once the script finishes it prints a summary like this:

```
---
score:          0.486000
pass_rate:      0.5600
tasks_passed:   14/25
avg_turns:      14.8
total_api_calls: 72
cost_estimate:  $1.44
```

You can extract the key metric from the log file:

```
grep "^score:" run.log
```

## Logging results

When an experiment is done, log it to `results.tsv` (tab-separated).

The TSV has a header row and 5 columns:

```
commit	score	pass_rate	status	description
```

1. git commit hash (short, 7 chars)
2. score achieved (e.g. 0.486000) — use 0.000000 for crashes
3. pass_rate (e.g. 0.5600) — use 0.0000 for crashes
4. status: `keep`, `discard`, or `crash`
5. short text description of what this experiment tried

Example:

```
commit	score	pass_rate	status	description
a1b2c3d	0.486000	0.5600	keep	baseline
b2c3d4e	0.592000	0.6400	keep	moved building to step 2
c3d4e5f	0.470000	0.5200	discard	removed show_playground tool
d4e5f6g	0.000000	0.0000	crash	API timeout in learner simulation
```

## The experiment loop

The experiment runs on a dedicated branch (e.g. `autoresearch/mar9`).

LOOP FOREVER:

1. Look at the git state: the current branch/commit we're on
2. Tune `tutor.py` with an experimental idea.
3. git commit
4. Run the experiment: `uv run evaluate.py > run.log 2>&1`
5. Read out the results: `grep "^score:\|^pass_rate:\|^tasks_passed:" run.log`
6. If the grep output is empty, the run crashed. Run `tail -n 50 run.log` to read the stack trace and attempt a fix.
7. Record the results in the tsv (do not commit results.tsv)
8. If score improved (higher), you "advance" the branch, keeping the git commit
9. If score is equal or worse, you git reset back to where you started

**Crashes**: If a run crashes (API error, bug, etc.), use your judgment: If it's easy to fix, fix and re-run. If the idea is broken, skip it and move on.

**Cost awareness**: Each run makes ~60-80 API calls ($1-2). Be intentional with experiments, not random. Form a hypothesis, test it, learn from the result.

**Experiment ideas** (starting points, not exhaustive):
- Reorder the teaching sequence (what if building comes before explaining?)
- Try removing tools (is show_comparison even necessary?)
- Change when the tutor intervenes vs. lets them struggle
- Test different opening strategies (ask about their life vs. jump into a demo)
- Try different failure demos (sycophancy vs. hallucination — which lands harder?)
- Vary how much the tutor explains vs. shows
- Test: does the tutor naming what it's doing help or hurt?
- Ablation: remove the system prompt explanation entirely
- Try radical simplification (shortest prompt that maintains score)
- Test persona-adaptive strategies vs. one-size-fits-all
- Experiment with the [ASSESS] timing — earlier vs. later

**NEVER STOP**: Once the experiment loop has begun, do NOT pause to ask the human if you should continue. The human might be asleep. You are autonomous. If you run out of ideas, think harder — re-read the assessment rubrics, look at which personas/tasks fail most, try combining near-misses. The loop runs until the human interrupts you, period.
