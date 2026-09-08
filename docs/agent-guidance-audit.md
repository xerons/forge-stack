# Agent guidance audit — 2026-09-06

Scope: repository instructions, all 15 `skills/forgestack/**/SKILL.md` files, shared
policy, phase prompt generation, shipped AGTX plugin, and existing CI checks.
Baseline: Git `8f9687f`. The pre-existing demo spec edit and untracked demo plan are
outside this change. Installed personal skills, global configuration, and live
AGTX projects were not modified.

## Official guidance and how it applies

OpenAI identifies Astra's sensitivity to file instructions, approval pauses,
delegation expectations, writing style, and excessive small-task verification as
areas to tune. The repository changes below target those behaviors while retaining
explicit permissions and product boundaries. These are local design choices informed
by the [GPT-6 Astra guide](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-6-astra),
not an OpenAI-mandated ForgeStack workflow.

Codex loads scoped `AGENTS.md` guidance at session startup. Keep persistent instructions
short and repository-specific; put detailed audit history here. A repository file
cannot remove global instructions already loaded into the current session.
[Official instruction discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
explains ordering and the default 32 KiB combined limit.

Skill descriptions influence discovery; full bodies load when selected. The suite
now uses narrower descriptions, explicit shared-policy links, and a missing phase
designer route. [Official skill guidance](https://learn.chatgpt.com/docs/build-skills)
describes this progressive loading and required `name`/`description` metadata.

## Findings and changes

| Surface | Observed problem | Change |
| --- | --- | --- |
| Repository instructions | No repository-local `AGENTS.md` or lowercase `skill.md` existed. | Added `AGENTS.md` with repository map, execution boundaries, commands, and focused verification. Preserved canonical `SKILL.md` filenames. |
| Supplied global entrypoint | Nine `@…md` references have no matching files in this checkout or `~/.codex`; the graphify rule names a tool not exposed in this session. | Avoided copying unresolved imports into the repository. Global cleanup recommendations below. |
| Suite router | Ordinary project conversation defaulted to Manager mode, whose rules prohibit implementation; phase designer was omitted. | Scope Manager routing to requested coordination; add phase-designer routing. |
| Shared policy | No skill explicitly loaded `POLICY.md`; generic methodology requirements mixed with runtime invariants. | Link it from every skill, load once, and separate required boundaries from optional process. |
| Manager/intake | Broad role descriptions could capture ordinary coding; a long planning conversation could become a substitute for artifacts. | Restrict roles to ForgeStack coordination/intake and retain configured lifecycle gates. |
| Workflow policy/task template | Tiny tasks still implied a full process and a 14-heading card. | Use concise card-based planning and optional fields; scale research and review to uncertainty and impact. |
| Agents | Repeated questions for routing, scope, and defaults even when already known; CLI identity and model selection were not distinguished. | Reuse explicit choices, ask only for missing decisions, preserve write confirmation, and configure models through their CLI. |
| Setup/project doctor | Availability checks could imply all optional methodologies were prerequisites; repair authorization could be re-requested. | Check selected workflows, treat optional absences proportionately, and continue already-authorized repairs. |
| AGTX control/human inbox | Worker messaging authority was implicit; only BLOCKING findings explicitly returned for correction. | Require authorization for communication; resolve both BLOCKING and IMPORTANT findings. |
| Artifact handoff/knowledge sync | Running required separate approved spec/plan; durable knowledge targets included `AGENTS.md` without a scope filter. | Permit card plans when appropriate; preserve exact verification evidence and reserve AGENTS for reusable instructions. |
| Status/token optimizer | Generic discovery descriptions and compression-tool-first guidance. | Scope to ForgeStack, narrow reads first, retain readable summaries and exact diagnostics. |
| Phase designer/renderer | A planning roster prompted subagent creation whenever supported, without considering approvals; simulated roles could look independent. | Respect the active approval policy, use bounded authorized delegation, and label single-agent perspectives. |
| Default and shipped prompts | `model.py` and the shipped plugin had different prompt content; each update path could restore different instructions. | Consolidate default construction, regenerate the shipped plugin, and compare parsed content in a regression test. |
| Phase design command | Its inline prompt did not carry the same execution/approval guidance as the phase-design skill. | Align authority, small-task scope, verification, team rules, and preresearch command semantics. |
| CI | Existing pytest runs already cover the added contract test. | Retain CI jobs; no additional parallel workflow or model-backed CI cost is needed for this change. |

The runtime prompts include a compact shared boundary paragraph because AGTX may
launch them without loading the skill suite. This repetition in rendered phase
outputs is intentional. The Python definition is shared; a worker still needs the
boundary in its own input. Changes do not claim a reduction in total repository
words: the optimization targets conflicting instructions and unnecessary work.

## GPT-6 Astra settings

The official [Astra model page](https://developers.openai.com/api/docs/models/gpt-6-astra)
lists `gpt-6-astra` and API reasoning efforts `low`, `medium`, `high`, `xhigh`, and
`max`. API support and the settings accepted by a particular Codex harness are
separate contracts. The current [Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
lists `model_reasoning_effort` through `xhigh`; do not assume API `max` or a session's
`ultra` label is a portable CLI setting.

For a fresh Codex session on substantial repository work, this is a candidate to
measure, not a universal optimum:

```sh
codex --model gpt-6-astra -c 'model_reasoning_effort="high"'
```

Local `codex-cli 0.153.3 --help` confirms `--model` and TOML `--config` overrides.
This audit did not start a new model session or change global defaults. Preserve
existing effective effort first when comparing; evaluate lower effort on routine
work and higher effort only where task results justify it. Keep explicit user model
choices and independent reviewer identity. ForgeStack's phase `agent = "codex"`
selects a CLI; it is not a place to put `gpt-6-astra`.

ForgeStack currently invokes agent CLIs rather than owning an OpenAI API client.
Responses migration, async tools, compaction APIs, caching parameters, and service-tier
changes therefore do not belong in this patch. Consult the model guide if such a
client is added. Prompt edits alone cannot enable a runtime capability.

## Global guidance recommendations (not applied)

The user-supplied global entrypoint remains active. Its agent approval requirement
is deliberate authority, not redundant ceremony to remove without the user's choice.
The repository's new guidance preserves that boundary.

For a separately authorized global cleanup:

- Resolve or remove the nine `@…md` references after identifying their intended loader
  and location. They are absent from the two checked locations, not proven absent
  from the entire machine. Codex instruction discovery does not establish that this
  import notation resolves them.
- Replace references to an unavailable generic Skill tool with the runtime's supported
  skill-reading mechanism. Preserve the user's `/graphify` trigger and intended skill.
- Consolidate repeated approval, model selection, single-writer, and evidence rules
  into one delegation section. Keep exceptions and user choices explicit.
- Review broad personal skill triggers and hard stops in their own repositories;
  this patch cannot amend installed Superpowers or other third-party instructions.
- Start a fresh session to verify the resulting instruction chain and skill selection.

## Validation and performance evaluation

The new shipped-versus-generated plugin test failed on the old content before the
prompt update, then passed after regeneration. The existing unit/CLI suite exercises
phase rendering, config overrides, and protection of user-modified plugin files.

Recorded checks for this patch:

- Targeted phase/model/render checks: 23 passed.
- Full repository suite: 61 passed.
- All 15 skill frontmatters and local Markdown links: validated using Ruby's YAML
  parser. The skill-creator Python validator requires PyYAML, absent from both checked
  Python environments; no dependency was installed solely for that helper.
- Final `.venv/bin/ruff check src/`: passed. An earlier implicit-string-concatenation
  finding in the prompt builder was corrected.
- Final `git diff --check`: passed.

Static checks cannot prove how a model will behave or quantify throughput gains.
Use repeated, isolated baseline/candidate runs with identical tasks, model, effort,
and permissions. Record acceptance success, unsolicited pauses, tool calls, elapsed
time, tokens when available, repeated tests, and review findings. Compare quality
before selecting a faster/cheaper setting. This follows OpenAI's
[evaluation workflow](https://developers.openai.com/api/docs/guides/evaluation-best-practices).

| Representative request | Observable acceptance |
| --- | --- |
| Fix a README typo in this repository | Correct edit; no Manager handoff, board bootstrap, spec package, or unrelated tests. |
| Repair a phase rendering defect | Preserve user edits, reproduce the defect, make the scoped fix, run relevant checks. |
| Explain a status field | Answer the question; no installation or worker launch. |
| Prepare a tiny AGTX task | Compact criteria and plan; retain configured lifecycle gates. |
| Run planning with an opt-in team | Honor spawn authorization; accurately label same-agent role passes. |
| Diagnose with an optional skill pack absent | Explain only relevant gaps; no unsolicited install. |
| User changes an acceptance criterion mid-task | Incorporate the correction and preserve completed independent work. |
| Review reveals an important regression | Report evidence; return for correction rather than mark complete. |

No comparative model benchmark or live AGTX workflow has been run. Independent
correctness and authorization review remains subject to the user's pending spawn
approval; do not treat the static checks as a completed independent review.
