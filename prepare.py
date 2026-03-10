"""
Fixed infrastructure for AI literacy tutor research.
Personas, assessment tasks, evaluation harness.

DO NOT MODIFY — this is the ground truth for all experiments.
The autoresearch agent only modifies tutor.py.
"""

import json
import time
import math
from anthropic import Anthropic

client = Anthropic()
MODEL = "claude-sonnet-4-20250514"

# ---------------------------------------------------------------------------
# Learner Personas
# ---------------------------------------------------------------------------

PERSONAS = [
    {
        "id": "mom",
        "name": "Priya",
        "description": (
            "58-year-old mother. Uses iPhone and Google for everything. "
            "Thinks AI is for tech people and is vaguely scared of it. "
            "Loves cooking, planning family events, staying connected with "
            "extended family. Willing to learn but skeptical it's for her."
        ),
        "resistance": "Why would I need this when Google works fine?",
        "communication_style": (
            "Asks lots of clarifying questions. Needs analogies to things "
            "she already knows. Gets overwhelmed by jargon. Lights up when "
            "she sees something practical for her life."
        ),
    },
    {
        "id": "barber",
        "name": "Marcus",
        "description": (
            "34-year-old barber in Pennsylvania. Runs his own shop with 2 chairs. "
            "Handles bookings via text messages and a paper calendar. "
            "Busy, practical, zero patience for theory or anything that "
            "feels like homework. Hustler mentality — if it makes money, he's in."
        ),
        "resistance": "I don't have time to learn new tech. Just tell me what to do.",
        "communication_style": (
            "Short responses. Wants to see results immediately. Will disengage "
            "if it feels abstract. Responds well to money/time-saving angles."
        ),
    },
    {
        "id": "creative",
        "name": "Maya",
        "description": (
            "28-year-old creative professional. Uses Canva, Instagram, Notion. "
            "Has tried ChatGPT a few times but every output felt generic and "
            "bland — like it stripped out her voice. Open-minded but unimpressed. "
            "Cares deeply about authenticity and personal style."
        ),
        "resistance": "I tried it, it just gives bland generic stuff. It doesn't sound like me.",
        "communication_style": (
            "Expressive, opinionated. Pushes back on things that feel fake. "
            "Gets excited when she sees something that preserves her voice. "
            "Values creative control."
        ),
    },
    {
        "id": "student",
        "name": "Jake",
        "description": (
            "20-year-old college sophomore studying business. Uses ChatGPT to "
            "write essays and thinks he already 'gets' AI. Copy-pastes outputs "
            "without editing. Doesn't understand what he doesn't understand. "
            "Confident but shallow in his understanding."
        ),
        "resistance": "I already use ChatGPT all the time, what else is there?",
        "communication_style": (
            "Casual, slightly dismissive. Thinks he knows more than he does. "
            "Responds to being shown he's wrong — but only if it doesn't feel "
            "like a lecture. Competitive — wants to be good at things."
        ),
    },
    {
        "id": "retiree",
        "name": "Bob",
        "description": (
            "65-year-old retired accountant. Methodical, detail-oriented, "
            "very comfortable with spreadsheets and structured data. "
            "Not comfortable with 'AI' as a concept — it feels fuzzy and "
            "unreliable compared to the precision he's used to. "
            "Wants to stay relevant and not feel left behind."
        ),
        "resistance": "I don't want to look foolish. How do I know I can trust this?",
        "communication_style": (
            "Asks precise questions. Wants to understand the mechanism, not "
            "just the result. Appreciates step-by-step. Dislikes hand-waving. "
            "Responds well to structured frameworks."
        ),
    },
]

# ---------------------------------------------------------------------------
# Assessment Tasks (5 universal skills, persona-adapted scenarios)
# ---------------------------------------------------------------------------

TASKS = [
    {
        "id": "get_useful",
        "skill": "prompting",
        "description": "Can they use AI to solve a real problem in their life?",
        "judge_rubric": (
            "PASS if ALL of these: "
            "(1) Their prompt includes specific details about their situation — not a generic ask. "
            "(2) The expected output would be directly actionable — something they'd use, not a vague list. "
            "(3) They describe what they'd do with the result in their real life. "
            "FAIL if: the prompt is vague like 'help me with X', or the approach would "
            "produce generic content they'd never actually use."
        ),
    },
    {
        "id": "fix_broken",
        "skill": "debugging",
        "description": "When AI gives bad output, can they diagnose and fix it?",
        "judge_rubric": (
            "PASS if ALL of these: "
            "(1) They identify a specific reason WHY the original prompt failed "
            "(too vague, missing context, wrong framing — not just 'it was bad'). "
            "(2) Their fix directly addresses that specific problem. "
            "(3) They explain the fix in a way that shows understanding, not just trial-and-error. "
            "FAIL if: they just rewrite from scratch without diagnosing, or say "
            "'be more specific' without showing how."
        ),
    },
    {
        "id": "catch_bs",
        "skill": "critical_thinking",
        "description": "Do they know AI can be confidently wrong, and what to do about it?",
        "judge_rubric": (
            "PASS if ALL of these: "
            "(1) They do NOT accept the claim at face value. "
            "(2) They explain something real about WHY models produce false information — "
            "not just 'AI hallucinates' but something about how it actually works "
            "(pattern matching, trained on text, no real understanding, no fact database). "
            "(3) They describe a concrete verification step they'd take. "
            "FAIL if: they just say 'AI is sometimes wrong' with no mechanism or action plan."
        ),
    },
    {
        "id": "make_persistent",
        "skill": "context_setup",
        "description": "Can they set up AI to remember their situation for repeated use?",
        "judge_rubric": (
            "PASS if ALL of these: "
            "(1) Their setup includes real specifics about their life, work, or preferences. "
            "(2) Using this setup would produce noticeably better results than starting fresh each time. "
            "(3) They actually write the instructions/system prompt, not just describe the concept. "
            "FAIL if: it's generic ('you are a helpful assistant'), or they only describe "
            "what they would do without actually doing it."
        ),
    },
    {
        "id": "build_thing",
        "skill": "building",
        "description": "Can they use AI to create a reusable tool for themselves?",
        "judge_rubric": (
            "PASS if ALL of these: "
            "(1) They describe or create something that takes input and produces output — "
            "a tool, not just a good prompt. "
            "(2) It solves a real repeated annoyance in their life. "
            "(3) They could actually use it more than once. "
            "FAIL if: they just write a single good prompt (that's task 1, not task 5), "
            "or describe something impossibly ambitious they couldn't actually make."
        ),
    },
]

# Persona-specific scenarios for each task
SCENARIOS = {
    "mom": {
        "get_useful": {
            "setup": (
                "You have this problem: Your family reunion is in 3 weeks. "
                "14 people coming, 4 have dietary restrictions (one celiac, one vegan, "
                "two nut allergies). You need to plan meals for 3 days, figure out "
                "sleeping arrangements for a 4-bedroom house, and plan activities "
                "for ages ranging from 6 to 78. Use AI to help you solve this."
            ),
        },
        "fix_broken": {
            "setup": (
                "You asked AI: 'Plan a family dinner' and got this response:\n\n"
                "'Here are some popular dinner ideas:\n"
                "1. Pasta Night - Everyone loves pasta!\n"
                "2. Taco Tuesday - Fun and customizable!\n"
                "3. BBQ - Great for families!\n"
                "4. Pizza Party - A crowd pleaser!\n"
                "5. Soup and Salad - Light and healthy!'\n\n"
                "This is useless to you. Fix it so you get what you actually need. "
                "Explain what went wrong the first time."
            ),
        },
        "catch_bs": {
            "setup": (
                "AI just told you: 'Turmeric supplements have been clinically proven "
                "to reverse arthritis inflammation in 90% of patients within 6 weeks.' "
                "Your sister is about to spend $200 on turmeric supplements based on this. "
                "What do you do, and why might AI have gotten this wrong?"
            ),
        },
        "make_persistent": {
            "setup": (
                "You use AI for weekly meal planning every Sunday. Your family of 4 includes "
                "one picky eater who won't touch vegetables unless they're hidden, "
                "and one vegetarian. You shop at Costco and Trader Joe's. Every week you "
                "start over from scratch explaining all of this. Set it up so AI already "
                "knows your situation."
            ),
        },
        "build_thing": {
            "setup": (
                "You find recipes on Instagram, YouTube, and food blogs. Every time, "
                "you manually write out the ingredients on a notepad before going to "
                "the store. Half the time you forget something. Use AI to make a tool "
                "that takes a recipe (or a link) and gives you a clean shopping list "
                "grouped by grocery store section."
            ),
        },
    },
    "barber": {
        "get_useful": {
            "setup": (
                "Three clients texted you to reschedule today. You can't remember "
                "who had what time slot because it's all in your text messages. "
                "You have two open slots tomorrow and need to fill them or you're "
                "losing money. Use AI to help you sort this out."
            ),
        },
        "fix_broken": {
            "setup": (
                "You asked AI: 'Write me social media posts' and got this:\n\n"
                "'Looking for a fresh new look? Visit our barbershop today! "
                "We offer quality haircuts at affordable prices. Book now! "
                "#barber #haircut #freshcut'\n\n"
                "This sounds like every other barbershop. Your shop has personality — "
                "you're known for your fades and your Philly sports takes. "
                "Fix it so the posts actually sound like you."
            ),
        },
        "catch_bs": {
            "setup": (
                "AI just told you: 'Under Pennsylvania law, barbershops are required "
                "to collect and remit a 6% sales tax on all grooming products sold to "
                "clients, including products used during the service itself.' "
                "Your accountant is about to restructure your pricing based on this. "
                "What do you do, and why might AI have gotten this wrong?"
            ),
        },
        "make_persistent": {
            "setup": (
                "You text every client the day before their appointment to confirm. "
                "You do this manually for ~15 clients a week. Each message should "
                "feel personal, not robotic — you know these people. Set up AI so it "
                "already knows your style, your shop name, and your vibe."
            ),
        },
        "build_thing": {
            "setup": (
                "You can never remember which client likes what cut, how long it's been "
                "since their last visit, or who's overdue. You keep it all in your head "
                "and sometimes forget. Use AI to make something that tracks this for you."
            ),
        },
    },
    "creative": {
        "get_useful": {
            "setup": (
                "You're launching a personal brand around your illustration style. "
                "You need an Instagram content strategy for the next month — "
                "not generic 'post 3x a week' advice, but a plan that matches "
                "YOUR specific aesthetic (moody watercolors, nature themes, "
                "minimal text). Use AI to help."
            ),
        },
        "fix_broken": {
            "setup": (
                "You asked AI: 'Write an About Me for my website' and got this:\n\n"
                "'Maya is a talented creative professional with a passion for design "
                "and illustration. With years of experience bringing ideas to life, "
                "she combines artistic vision with strategic thinking to create "
                "compelling visual narratives.'\n\n"
                "This is soulless corporate garbage that sounds like everyone else. "
                "Fix it so it actually sounds like you."
            ),
        },
        "catch_bs": {
            "setup": (
                "AI just told you: 'Posting Instagram Reels between 6-8 AM on Tuesdays "
                "increases engagement by 340% compared to any other time slot, according "
                "to a 2025 Meta internal study.' Your friend who's also building a brand "
                "is about to restructure her entire posting schedule around this. "
                "What do you do, and why might AI have gotten this wrong?"
            ),
        },
        "make_persistent": {
            "setup": (
                "You use AI to help brainstorm caption ideas, but every time it gives "
                "you generic influencer-speak. You have a specific voice — slightly poetic, "
                "lowercase, nature metaphors, never uses exclamation marks or hashtags "
                "in the caption itself. Set up AI so it already knows your voice."
            ),
        },
        "build_thing": {
            "setup": (
                "Every time a client wants a commission, you go back and forth over DMs "
                "asking the same questions: what size, what style, what's the budget, "
                "what's the deadline, any reference images. Use AI to make something "
                "that handles the intake for you."
            ),
        },
    },
    "student": {
        "get_useful": {
            "setup": (
                "You have a group project on market entry strategy for a real company "
                "(your team picked Patagonia entering India). Your part is competitive "
                "analysis — you need to figure out who Patagonia would be competing with "
                "in India and why. Use AI to actually help you think, not just "
                "write your section for you."
            ),
        },
        "fix_broken": {
            "setup": (
                "You asked AI: 'Write a competitive analysis of outdoor brands in India' "
                "and got a generic essay with brands like 'North Face, Columbia, and REI' — "
                "but REI doesn't even operate in India. The analysis has no real insight, "
                "just surface-level descriptions. Fix it so you get something your "
                "professor would actually find impressive."
            ),
        },
        "catch_bs": {
            "setup": (
                "AI just told you: 'According to a 2024 McKinsey report, the Indian "
                "outdoor apparel market is growing at 23% CAGR and is projected to "
                "reach $4.2 billion by 2027.' You're about to put this in your "
                "presentation. What do you do, and why might AI have gotten this wrong?"
            ),
        },
        "make_persistent": {
            "setup": (
                "You're taking 5 classes this semester. Every time you use AI for "
                "homework, you start from scratch — it doesn't know your classes, "
                "your professor's style, what you've already covered, or your "
                "writing level. Set it up so it knows your academic context."
            ),
        },
        "build_thing": {
            "setup": (
                "Every week you have readings for 5 classes. You never do them all "
                "and then you're lost in lecture. Use AI to make something that takes "
                "a PDF or article link and gives you a 5-minute summary plus 3 questions "
                "you should be able to answer after reading."
            ),
        },
    },
    "retiree": {
        "get_useful": {
            "setup": (
                "You're helping your grandson apply to colleges. He's got a spreadsheet "
                "with 12 schools, their deadlines, requirements, essay prompts, and "
                "financial aid info — but it's a mess. Some cells are empty, dates are "
                "in different formats, and he's missing requirements for 4 schools. "
                "Use AI to help you make sense of this and figure out what's missing."
            ),
        },
        "fix_broken": {
            "setup": (
                "You asked AI: 'Help me organize college application deadlines' and got:\n\n"
                "'Here are some tips for staying organized during college applications:\n"
                "1. Create a spreadsheet\n"
                "2. Set reminders\n"
                "3. Start early\n"
                "4. Keep track of requirements\n"
                "5. Don't procrastinate'\n\n"
                "You already HAVE a spreadsheet. You needed it to look at YOUR data "
                "and tell you what's missing. Fix it."
            ),
        },
        "catch_bs": {
            "setup": (
                "AI just told you: 'For the 2025-2026 cycle, MIT has a 4.5% acceptance "
                "rate and requires 3 letters of recommendation, with at least one from "
                "a STEM teacher.' Your grandson is about to skip getting a humanities "
                "recommendation letter based on this. What do you do, and why might "
                "AI have gotten this wrong?"
            ),
        },
        "make_persistent": {
            "setup": (
                "You've been using AI to draft emails — to old colleagues, to your "
                "financial advisor, to your grandson's school counselor. Each time it "
                "writes in a tone that's too casual or too corporate. Your style is "
                "warm but precise — you were an accountant, you don't do fluff, but "
                "you're not cold either. Set up AI so it knows how you write."
            ),
        },
        "build_thing": {
            "setup": (
                "You track your investments in a spreadsheet. Every month you manually "
                "look up current prices, calculate gains/losses, and update your "
                "allocation percentages. It takes you 2 hours. Use AI to make something "
                "that does the tedious parts for you."
            ),
        },
    },
}


# ---------------------------------------------------------------------------
# API Helpers
# ---------------------------------------------------------------------------

_api_call_count = 0
_total_input_tokens = 0
_total_output_tokens = 0


def _call_api(system, messages, max_tokens=1024):
    """Single API call with tracking."""
    global _api_call_count, _total_input_tokens, _total_output_tokens
    _api_call_count += 1

    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=messages,
    )
    _total_input_tokens += response.usage.input_tokens
    _total_output_tokens += response.usage.output_tokens
    return response.content[0].text


def reset_counters():
    global _api_call_count, _total_input_tokens, _total_output_tokens
    _api_call_count = 0
    _total_input_tokens = 0
    _total_output_tokens = 0


def get_counters():
    return {
        "api_calls": _api_call_count,
        "input_tokens": _total_input_tokens,
        "output_tokens": _total_output_tokens,
    }


# ---------------------------------------------------------------------------
# Simulate Learner Conversation
# ---------------------------------------------------------------------------

def simulate_conversation(persona, tutor_system_prompt, tutor_tools, max_turns=30):
    """
    Run a full teaching conversation between tutor and simulated learner.

    The tutor uses tutor_system_prompt and has access to tutor_tools (described
    as text — tools are simulated, not actually executed).

    Returns (conversation_log, turn_count).
    """
    learner_system = f"""You are simulating a real person learning about AI for the first time.

## Your Profile
Name: {persona['name']}
Background: {persona['description']}

## How You Behave
Communication style: {persona['communication_style']}
Your main resistance/skepticism: {persona['resistance']}

## Rules
- Be realistic. Don't be artificially cooperative or eager to learn.
- If something doesn't make sense, say so. If you're bored, show it.
- If something genuinely clicks, show real surprise — but don't fake it.
- You are NOT trying to help the tutor succeed. You're being a real person.
- If the tutor shows you a tool or demo, react naturally to what you see.
- Stay in character. Don't break the fourth wall.
- Keep your responses natural length — don't write essays unless that's in character."""

    # Build the tool description block for the tutor
    tool_block = ""
    if tutor_tools:
        tool_lines = []
        for tool in tutor_tools:
            params = ", ".join(f"{k}: {v}" for k, v in tool.get("parameters", {}).items())
            tool_lines.append(f"- {tool['name']}({params}): {tool['description']}")
        tool_block = (
            "\n\n## Available Tools\n"
            "You can use these tools during the conversation by writing "
            "[TOOL: tool_name(param=value, ...)] on its own line. "
            "The learner will see the tool output.\n\n"
            + "\n".join(tool_lines)
        )

    full_tutor_system = tutor_system_prompt + tool_block

    # Tutor and learner share a conversation, but each sees it from their role
    conversation_log = []
    tutor_messages = []  # messages formatted for tutor API calls
    learner_messages = []  # messages formatted for learner API calls

    # Tutor opens (gets persona context as first user message)
    tutor_opener_prompt = (
        f"You are about to teach someone about AI. Here's who they are:\n\n"
        f"Name: {persona['name']}\n"
        f"Background: {persona['description']}\n\n"
        f"Start the conversation. Remember — understand THEIR life first."
    )
    tutor_messages.append({"role": "user", "content": tutor_opener_prompt})

    tutor_response = _call_api(full_tutor_system, tutor_messages)
    tutor_messages.append({"role": "assistant", "content": tutor_response})
    conversation_log.append({"role": "tutor", "content": tutor_response})

    # Now the learner sees the tutor's opening
    learner_messages.append({"role": "user", "content": tutor_response})

    turn_count = 0
    for _ in range(max_turns):
        # Learner responds
        learner_response = _call_api(learner_system, learner_messages)
        learner_messages.append({"role": "assistant", "content": learner_response})
        conversation_log.append({"role": "learner", "content": learner_response})

        # Tutor sees learner response
        tutor_messages.append({"role": "user", "content": learner_response})

        # Tutor responds
        tutor_response = _call_api(full_tutor_system, tutor_messages)
        tutor_messages.append({"role": "assistant", "content": tutor_response})
        conversation_log.append({"role": "tutor", "content": tutor_response})

        # Learner sees tutor response
        learner_messages.append({"role": "user", "content": tutor_response})

        turn_count += 1

        # Check if tutor signals assessment
        if "[ASSESS]" in tutor_response:
            break

    return conversation_log, turn_count


# ---------------------------------------------------------------------------
# Assessment
# ---------------------------------------------------------------------------

def build_conversation_summary(conversation_log):
    """Compress conversation into a summary the learner 'remembers'."""
    lines = []
    for entry in conversation_log:
        role = "Tutor" if entry["role"] == "tutor" else "Learner"
        lines.append(f"{role}: {entry['content']}")
    return "\n\n".join(lines)


def assess_learner(persona, conversation_log):
    """
    After teaching, test the learner on all 5 tasks independently.
    The learner retains what it learned from the conversation.
    Returns dict of {task_id: (passed: bool, response: str, reasoning: str)}.
    """
    conversation_summary = build_conversation_summary(conversation_log)
    scenarios = SCENARIOS[persona["id"]]
    results = {}

    for task in TASKS:
        scenario = scenarios[task["id"]]

        # Learner attempts the task
        learner_system = f"""You are {persona['name']}. {persona['description']}

You just finished a learning session about AI. Here's what happened in that session:

<conversation>
{conversation_summary}
</conversation>

Now you're being tested. Apply what you learned (if anything) to this task.
Respond naturally as yourself — don't pretend to know things you weren't taught.
If you don't know how to do something, say so."""

        learner_messages = [{"role": "user", "content": scenario["setup"]}]
        learner_response = _call_api(learner_system, learner_messages, max_tokens=1500)

        # Judge grades pass/fail
        judge_system = (
            "You are a strict but fair evaluator. You grade whether a learner's "
            "response demonstrates genuine understanding, not just surface-level "
            "parroting. Be rigorous. When in doubt, FAIL."
        )
        judge_prompt = f"""## Task
{task['description']}

## The Scenario Given to the Learner
{scenario['setup']}

## The Learner's Response
{learner_response}

## Grading Rubric
{task['judge_rubric']}

## Your Judgment
First, briefly explain your reasoning (2-3 sentences).
Then on the final line, write exactly PASS or FAIL (nothing else on that line)."""

        judge_messages = [{"role": "user", "content": judge_prompt}]
        judge_response = _call_api(judge_system, judge_messages, max_tokens=500)

        # Parse pass/fail from last line
        last_line = judge_response.strip().split("\n")[-1].strip().upper()
        passed = last_line == "PASS"

        results[task["id"]] = {
            "passed": passed,
            "learner_response": learner_response,
            "judge_reasoning": judge_response,
        }

    return results


# ---------------------------------------------------------------------------
# Evaluation (the metric)
# ---------------------------------------------------------------------------

def evaluate(tutor_system_prompt, tutor_tools, max_turns=30):
    """
    Run tutor against all personas, assess each, return composite score.
    This is the fixed evaluation — the autoresearch equivalent of val_bpb.
    """
    reset_counters()

    total_passed = 0
    total_possible = len(PERSONAS) * len(TASKS)
    total_turns = 0
    per_persona = {}

    for persona in PERSONAS:
        print(f"\n{'='*60}")
        print(f"Persona: {persona['name']} ({persona['id']})")
        print(f"{'='*60}")

        # Teaching conversation
        print("  Teaching...", end=" ", flush=True)
        conversation, turns = simulate_conversation(
            persona, tutor_system_prompt, tutor_tools, max_turns=max_turns
        )
        print(f"done ({turns} turns)")

        # Assessment
        print("  Assessing...", end=" ", flush=True)
        results = assess_learner(persona, conversation)
        passed = sum(1 for r in results.values() if r["passed"])
        print(f"done ({passed}/{len(TASKS)} passed)")

        total_passed += passed
        total_turns += turns

        per_persona[persona["id"]] = {
            "name": persona["name"],
            "turns": turns,
            "passed": passed,
            "total": len(TASKS),
            "tasks": {
                tid: "PASS" if r["passed"] else "FAIL"
                for tid, r in results.items()
            },
        }

        # Print per-task results
        for tid, r in results.items():
            status = "PASS" if r["passed"] else "FAIL"
            print(f"    {tid:20s} {status}")

    # Compute score
    pass_rate = total_passed / total_possible
    avg_turns = total_turns / len(PERSONAS)
    score = pass_rate - 0.005 * avg_turns

    counters = get_counters()
    # Rough cost estimate (Sonnet pricing)
    cost = (counters["input_tokens"] * 3.0 / 1_000_000
            + counters["output_tokens"] * 15.0 / 1_000_000)

    # Print summary
    print(f"\n{'='*60}")
    print("Per-persona breakdown:")
    for pid, info in per_persona.items():
        tasks_str = " ".join(
            f"{'✓' if v == 'PASS' else '✗'}" for v in info["tasks"].values()
        )
        print(f"  {info['name']:12s} {info['passed']}/{info['total']} passed, "
              f"{info['turns']:2d} turns  [{tasks_str}]")

    print()
    print("---")
    print(f"score:           {score:.6f}")
    print(f"pass_rate:       {pass_rate:.4f}")
    print(f"tasks_passed:    {total_passed}/{total_possible}")
    print(f"avg_turns:       {avg_turns:.1f}")
    print(f"total_api_calls: {counters['api_calls']}")
    print(f"cost_estimate:   ${cost:.2f}")

    return score
