---
name: forgestack
description: Modular skill suite for the ForgeStack Manager-first workflow stack.
---

# ForgeStack Suite Router

This is the main entry point and router for the forgestack skill suite.
The architecture separates concerns:
- **Manager (Coordinator)**: Coordinates the human-facing workflow.
- **AGTX (Authority)**: Authoritative Kanban / lifecycle / worktree / worker controller.
- **Workers (Execution)**: Execute specific phases based on dynamic configuration.

**Do NOT eagerly load all sub-skills.** Load only the specific sub-skills needed for the current task.

## Routing Guide

- **Initialize / bootstrap / repair project**: Route to `setup/SKILL.md`
- **Configure agents / CLIs / routing**: Route to `agents/SKILL.md`
- **New issue / feature / grooming**: Route to `manager/SKILL.md` and then `intake/SKILL.md`
- **Decide workflow process**: Route to `workflow-policy/SKILL.md`
- **Create standard task/card**: Route to `task-template/SKILL.md`
- **Operate AGTX (create, move, start, stop)**: Route to `agtx-control/SKILL.md`
- **Waiting on human decisions**: Route to `human-inbox/SKILL.md`
- **Check board status / what's next**: Route to `status/SKILL.md`
- **Pass phase outputs forward**: Route to `artifact-handoff/SKILL.md`
- **Save durable knowledge**: Route to `knowledge-sync/SKILL.md`
- **Optimize token/context (too noisy)**: Route to `token-optimizer/SKILL.md`
- **Diagnose broken setup**: Route to `project-doctor/SKILL.md`

For normal project conversation, default to `manager/SKILL.md`.
