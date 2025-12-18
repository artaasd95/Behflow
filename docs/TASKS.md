# Project Tasks & TODOs

This file enumerates actionable tasks and improvements for the Behflow project.

## High priority

- [ ] Implement the actual agent invocation in `src/backend/app/api/routers/chat.py` (replace the placeholder response with a call to `behflow_agent` and proper error handling).
- [ ] Implement LangGraph graph construction and node wiring in `src/behflow_agent`.
- [ ] Add integration tests for Task model and timezone/Jalali conversions.

## Medium priority

- [ ] Integrate LLM providers (OpenAI, Anthropic, etc.) with configuration and fallback behavior.
- [ ] Add CI linting and test runs (GitHub Actions recommended).

## Low priority

- [ ] Improve documentation and examples in `src/behflow_agent/`.
- [ ] Consider Docker image size trade-offs when removing pip cache flags.

> Notes:
> - 2025-12-18: `--no-cache-dir` was removed from the backend Dockerfile per request; be mindful that this can increase image layer sizes.
> - See `docs/CHANGES.md` for recent changes.
