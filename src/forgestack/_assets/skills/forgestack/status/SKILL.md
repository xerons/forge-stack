---
name: forgestack-status
description: Summarize ForgeStack/AGTX board progress, blockers, and the next action.
---

Read [shared policy](../POLICY.md) once per session when using this skill.

# Status Sub-skill

Provide an engineering-manager-style board summary.

**Answer:** What is running? Blocked? Needs me? Finished? Parallelizable? State of feature? What's next?

**Summarize:** Task, phase, assigned worker, state, blockers, pending human input, review findings, dependencies, recommended next action.

Avoid raw AGTX dumps unless requested. Default to compact status summaries. Retrieve per-task details only when necessary.
