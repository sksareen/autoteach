# Project notes

- Always use OpenRouter for model calls, authenticated with `OPENROUTER_API_KEY`. Never call provider APIs directly or require `ANTHROPIC_API_KEY`/`OPENAI_API_KEY`.
- All model calls go through `llm.call()` in `llm.py`.
