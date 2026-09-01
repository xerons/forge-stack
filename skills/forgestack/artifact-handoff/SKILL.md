---
name: forgestack-artifact-handoff
description: Standardize inputs/outputs between phases.
---

# Artifact Handoff Sub-skill

Standardize inputs/outputs between phases.

- **Research**: Consumes brief, docs/code. Outputs findings, risks, questions, evidence.
- **Planning**: Consumes brief, research findings. Outputs spec, architecture decisions, acceptance criteria, implementation plan/decomposition.
- **Running**: Consumes approved spec, approved plan. Outputs code, tests, verification result, implementation summary.
- **Review**: Consumes spec, diff, tests, summary. Outputs BLOCKING / IMPORTANT / OPTIONAL findings, acceptance result.

**Guidelines:**
- Prefer existing project conventions. Suggested fallback: `docs/ai/` (`research/`, `specs/`, `plans/`, `reviews/`).
- Artifacts must be concise enough for phase handoffs without requiring the next worker to reread large transcripts.
