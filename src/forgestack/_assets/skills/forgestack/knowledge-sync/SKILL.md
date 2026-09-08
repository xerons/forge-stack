---
name: forgestack-knowledge-sync
description: Record durable ForgeStack project decisions and verified findings in existing project documentation.
---

Read [shared policy](../POLICY.md) once per session when using this skill.

# Knowledge Sync Sub-skill

Promote durable findings into Git-backed project knowledge.

**Targets:** `AGENTS.md`, `docs/architecture/`, `docs/decisions/`, `docs/ai/*`, or existing project wiki structure.

**Rules:**
- Do not copy raw agent transcripts. Extract durable facts/decisions.
- Preserve existing conventions.
- Create ADRs only for meaningful architecture decisions.
- Do not invent rationale. Distinguish task-local notes from permanent knowledge.
- Keep `AGENTS.md` limited to reusable repository instructions. Put task progress, model research, and long explanations in task artifacts or focused docs.
- Use durable knowledge to reduce repeated rediscovery in future tasks.
