---
name: forgestack-knowledge-sync
description: Promote durable findings into project knowledge.
---

# Knowledge Sync Sub-skill

Promote durable findings into Git-backed project knowledge.

**Targets:** `AGENTS.md`, `docs/architecture/`, `docs/decisions/`, `docs/ai/*`, or existing project wiki structure.

**Rules:**
- Do not copy raw agent transcripts. Extract durable facts/decisions.
- Preserve existing conventions.
- Create ADRs only for meaningful architecture decisions.
- Do not invent rationale. Distinguish task-local notes from permanent knowledge.
- **Do not auto-commit.**
- Use durable knowledge to reduce repeated rediscovery in future tasks.
