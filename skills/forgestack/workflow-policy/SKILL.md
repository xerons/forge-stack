---
name: forgestack-workflow-policy
description: Decide how much process a task needs.
---

# Workflow Policy Sub-skill

Decide the necessary process for a task based on ambiguity, familiarity, architectural/security impact, size, and risk.

- **Tiny / low-risk:** Planning -> Running -> Review
- **Normal:** Manager intake -> Planning -> Running -> Review
- **Uncertain:** Manager intake -> Research -> Planning -> Running -> Review
- **High-risk:** Research -> Planning -> Running -> enhanced Review -> QA/acceptance

**Guidelines:**
- Matt review/research should be conditional, not mandatory.
- Scale token optimization with workload (avoid ceremony for tiny tasks, conservative compression for security/debugging).
