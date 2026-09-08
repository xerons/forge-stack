---
name: phase-designer
description: Write per-phase purpose and prompt content for a ForgeStack workflow phase model, preserving AGTX grammar.
---

Read [shared policy](../POLICY.md) once per session when using this skill.

Write the CONTENT of ForgeStack workflow phases (the model has already been scaffolded:
keys are fixed to research/planning/running/review/preresearch).

For each phase you are handed:

1. State the phase's `purpose` in one paragraph: what the agent in this phase must
   produce/decide, and what it must NOT do.
2. For agent phases, write a complete `prompt` string that starts with `Task:\n{task}` and guides the
   phase agent: the deliverable, scope boundaries, and acceptance evidence; use a fixed sequence
   only where correctness requires it. Keep it prompt-token-lean; correctness over verbosity.
3. Use the planning `team` as design context. The renderer appends role-pass and
   requirements × roles coverage matrix instructions, including spawn authorization
   and accurate labeling of single-agent perspectives. Do not duplicate that block
   in the prompt or run the team while designing the phase.
4. Use listed `skills` as context for phase outcomes. The renderer appends available
   skill-pack references; do not duplicate that list or require unavailable tooling.

Write prompts that preserve user steering, continue authorized work, ask only about
material unresolved decisions, and scale verification to risk. Preserve external-action
approvals. For `preresearch`, preserve its command semantics rather than turning it into
an agent conversation. Do not execute the workflow while designing it.

Return ONLY a fenced TOML block, one `[[workflow.phases]]` entry per phase, with `key`
matching the scaffolded key exactly. Do not invent new keys.
