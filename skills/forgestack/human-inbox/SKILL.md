---
name: forgestack-human-inbox
description: Aggregate worker questions and escalations for human decisions.
---

# Human Inbox Sub-skill

Aggregate worker questions/escalations.

**Behavior:**
- Inspect blocked/waiting tasks.
- Collect relevant questions and group related decisions.
- Classify: product decision, architecture decision, technical clarification, approval, blocker.
- Include recommendations when useful.
- Show concise context, not raw transcript.
- Route human answer back to correct worker.
- Record durable decisions through `knowledge-sync`.
- **Do not** overload the user with full terminal transcripts. Fetch deeper evidence only when needed.
