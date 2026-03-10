"""
Runner script. Imports tutor config, runs evaluation.
Usage: uv run evaluate.py
"""

from tutor import SYSTEM_PROMPT, TOOLS
from prepare import evaluate

if __name__ == "__main__":
    evaluate(SYSTEM_PROMPT, TOOLS)
