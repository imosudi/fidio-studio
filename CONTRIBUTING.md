# Contributing Guidelines & Architectural Standards — Fídíò Studio

Welcome to the Fídíò Studio repository! This document outlines code conventions, architectural boundaries, and guidelines for human contributors and automated coding agents.

---

## 1. Core Architectural Guidelines

- **Follow AGENTS.md:** `AGENTS.md` is the authoritative source for module boundaries, package relationships, and agent execution order.
- **Modular Monolith Integrity:** Keep domain logic inside `packages/domain` completely decoupled from API frameworks, database ORMs, or provider SDKs.
- **Provider Abstractions:** Never call external AI services (OpenRouter, ElevenLabs, Stability) directly inside API handlers. Implement abstract provider interfaces in `packages/domain` and concrete adapters in `packages/providers`.
- **Asynchronous Execution:** Long-running LLM script planning, image generation, audio processing, or FFmpeg composition MUST run asynchronously in worker background tasks (`services/worker`).

---

## 2. Code Quality & Verification

- **Linting & Formatting:** All Python code must comply with `ruff` and `mypy` static type checking. All TypeScript/React frontend code must pass `eslint` and `prettier`.
- **Testing Required:** Every pull request or agent sub-task implementation must include unit or integration tests in `tests/`.
- **Mock Adapters First:** Ensure all new AI provider interfaces include a corresponding `DevMock` adapter so tests can execute offline without cost.
