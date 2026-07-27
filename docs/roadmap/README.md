# Solo Company Platform Roadmap

This folder turns the source document into an implementation plan for a lean, modular web platform.

Start here:

1. [Master plan](./00-master-plan.md)
2. [Phase 1 — Single-company MVP](./01-phase-1-single-company-mvp.md)
3. [Phase 2 — Models, knowledge, skills, and tools](./02-phase-2-models-knowledge-skills-tools.md)
4. [Phase 3 — Safe autonomy and quality](./03-phase-3-safe-autonomy-and-quality.md)
5. [Phase 4 — Multi-company portfolio](./04-phase-4-multi-company-portfolio.md)
6. [Phase 5 — Production readiness](./05-phase-5-production-readiness.md)

The phases are gates, not deadlines. Do not start the next phase until the current phase's exit criteria pass.

The plan distinguishes two kinds of models:

- **Coding models:** GPT and Gemini 3.1 Pro are used to build separate modules.
- **Runtime models:** frontier APIs and local Ollama models are used by the company's agents.

Those choices are independent. A module written by Gemini can still call a GPT runtime model, and vice versa.

Coding-model ownership is based only on task difficulty and risk. GPT may own several consecutive complex modules, while Gemini may own several consecutive bounded modules. Alternating models is not a planning goal.
