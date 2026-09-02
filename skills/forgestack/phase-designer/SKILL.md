---
name: phase-designer
description: Write per-phase purpose and prompt content for a ForgeStack workflow phase model, preserving AGTX grammar.
---

Write the CONTENT of ForgeStack workflow phases (the model has already been scaffolded:
keys are fixed to research/planning/running/review/preresearch).

For each phase you are handed:

1. State the phase's `purpose` in one paragraph: what the agent in this phase must
   produce/decide, and what it must NOT do.
2. Write a complete `prompt` string that starts with `Task:\n{task}` and guides the
   phase agent: numbered Do items, explicit Do NOT items, and scoped acceptance-output
   expectations. Keep it prompt-token-lean; correctness over verbosity.
3. If the phase lists a `team` (planning only, opt-in): run one explicit role pass per
   member (deliverables, owned requirements, risks, commonly-overlooked items), delegate
   each pass to an internal sub-agent when the agent CLI supports it, and end with a
   requirements × roles coverage matrix flagging uncovered requirements as gaps.
4. If the phase lists `skills`: reference them inside the prompt as opportunistically
   available discipline, never as vendored assets.

Return ONLY a fenced TOML block, one `[[workflow.phases]]` entry per phase, with `key`
matching the scaffolded key exactly. Do not invent new keys.
