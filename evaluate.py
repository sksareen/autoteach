"""
Runner script. Loads the coach, runs the fixed evaluation.
Usage: uv run evaluate.py
"""

from coach import SYSTEM_PROMPT
from prepare import evaluate

if __name__ == "__main__":
    evaluate(SYSTEM_PROMPT)
