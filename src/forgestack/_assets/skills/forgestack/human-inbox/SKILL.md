---
name: forgestack-human-inbox
description: Collect blocked ForgeStack task questions and route authorized human decisions to workers.
---

Read [shared policy](../POLICY.md) once per session when using this skill.

# Human Inbox Sub-skill

Aggregate worker questions/escalations.

**Behavior:**
- Inspect blocked/waiting tasks.
- Collect relevant questions and group related decisions.
- Classify: product decision, architecture decision, technical clarification, approval, blocker.
- Include recommendations when useful.
- Show concise context, not raw transcript.
- Route the answer to the correct worker when the user has authorized that communication; collecting questions alone does not authorize sending messages.
- Record durable decisions through `knowledge-sync`.
- **Do not** overload the user with full terminal transcripts. Fetch deeper evidence only when needed.
