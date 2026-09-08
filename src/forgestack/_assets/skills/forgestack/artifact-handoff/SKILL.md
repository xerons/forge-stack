---
name: forgestack-artifact-handoff
description: Prepare concise, evidence-backed handoffs between ForgeStack workflow phases.
---

Read [shared policy](../POLICY.md) once per session when using this skill.

# Artifact Handoff Sub-skill

Standardize inputs/outputs between phases.

- **Research**: Consumes brief, docs/code. Outputs findings, risks, questions, evidence.
- **Planning**: Consumes brief and any research findings. Outputs acceptance criteria and a plan in the card, with separate specification or architecture artifacts when warranted.
- **Running**: Consumes the task acceptance criteria and required approved planning artifacts; a small task may keep its plan in the card. Outputs code, tests, verification result, implementation summary.
- **Review**: Consumes acceptance criteria, required planning artifacts, diff, tests, and summary. Outputs BLOCKING / IMPORTANT / OPTIONAL findings with file/evidence/impact, acceptance result, and review independence.

**Guidelines:**
- Prefer existing project conventions. Suggested fallback: `docs/ai/` (`research/`, `specs/`, `plans/`, `reviews/`).
- Include changed/examined files, actual commands and results, assumptions, unresolved risks, and next action. Link exact evidence instead of copying full transcripts. Do not report completion while BLOCKING or IMPORTANT findings remain unresolved.
