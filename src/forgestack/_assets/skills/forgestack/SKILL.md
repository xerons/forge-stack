---
name: forgestack
description: Operate or configure the ForgeStack Manager and AGTX workflow; route to the relevant ForgeStack sub-skill.
---

# ForgeStack Suite Router

Read [POLICY.md](POLICY.md) once, then select the relevant sub-skill.
The architecture separates concerns:
- **Manager (Coordinator)**: Coordinates the human-facing workflow.
- **AGTX (Authority)**: Authoritative Kanban / lifecycle / worktree / worker controller.
- **Workers (Execution)**: Execute specific phases based on dynamic configuration.

**Do NOT eagerly load all sub-skills.** Load only the specific sub-skills needed for the current task.

## Routing Guide

- **Initialize / bootstrap project**: Route to `setup/SKILL.md`
- **Configure agents / CLIs / routing**: Route to `agents/SKILL.md`
- **New issue / feature / grooming**: Route to `manager/SKILL.md` and then `intake/SKILL.md`
- **Design phase prompts**: Route to `phase-designer/SKILL.md`
- **Decide workflow process**: Route to `workflow-policy/SKILL.md`
- **Create standard task/card**: Route to `task-template/SKILL.md`
- **Operate AGTX (create, move, start, stop)**: Route to `agtx-control/SKILL.md`
- **Waiting on human decisions**: Route to `human-inbox/SKILL.md`
- **Check board status / what's next**: Route to `status/SKILL.md`
- **Pass phase outputs forward**: Route to `artifact-handoff/SKILL.md`
- **Save durable knowledge**: Route to `knowledge-sync/SKILL.md`
- **Optimize token/context (too noisy)**: Route to `token-optimizer/SKILL.md`
- **Diagnose broken setup**: Route to `project-doctor/SKILL.md`

Use `manager/SKILL.md` for requested Manager coordination. Ordinary coding or questions
about this repository do not automatically enter Manager mode or start AGTX workers.
