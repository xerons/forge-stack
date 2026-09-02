# Customizable Workflow Phase Model — Design

**Date:** 2026-09-02
**Status:** Approved (Approach A)
**Builds on:** ForgeStack v0.1 (config source of truth, adapter registry, AGTX plugin)

## 1. Purpose

Let the user customize ForgeStack's workflow phase model through a setup wizard:

- which phases exist (within AGTX's fixed lane grammar),
- what each phase is (label, purpose, prompt template),
- which skill packs it uses,
- which agent CLI runs it,
- and the flow shape (optional research lane, cyclic review→planning, one-time preresearch hook),
- plus a **multidisciplinary sprint-planning simulation** (optional, **disabled by default**): an opt-in role `team` on the planning phase whose members independently review a story so task breakdowns don't lose, miss, or overlook work. Default remains the plain single-agent planning prompt — the team simulation costs extra tokens and is only enabled when the user opts in.

The user co-designs content with the setup agent; shape decisions stay deterministic in the CLI.

## 2. Constraints (from AGTX upstream, verified 2026-09-02)

AGTX is workflow authority and is NOT replaced. AGTX's contract bounds the model:

1. **Fixed board lanes**: `backlog → planning → running → review → done`; research is an extra optional lane (`R` key). Done/Backlog structural.
2. **Per-phase agent routing is fixed to 4 keys**: `default_agent` + `[agents] research/planning/running/review` overrides (global `~/.config/agtx/config.toml` or project `.agtx/config.toml`).
3. **Plugin schema** (`plugin.toml`, global `~/.config/agtx/plugins/<name>/` or project `.agtx/plugins/<name>/`): `name`, `description`, `cyclic`, `supported_agents`, `init_script`, `copy_dirs`, `copy_files`, `[artifacts]`, `[commands]`, `[prompts]`, `[prompt_triggers]`, `[copy_back]`, `[[auto_dismiss]]`. Phase reachable from Backlog only if its command/prompt contains `{task}`. `preresearch` = one-time project-setup command on first Research. Custom skills ship in `skills/<name>/SKILL.md`.
4. Prompt placeholders: `{task}`, `{task_id}`, `{phase}`.

**Design implication**: customization is content-level within the 4-lane + research grammar. ForgeStack does not invent lane names; it decides WHICH phases exist (subset/order), their content (prompt/command/artifact/skill), cyclic on/off, and per-phase agent within the named keys.

## 3. Decision: source of truth

ForgeStack config is the single source of truth. A command re-renders the AGTX `plugin.toml` + `[agents]` wiring from it. AGTX remains authority at runtime; ForgeStack owns the model that generates its plugin.

Scope levels: **both** global (machine default) and per-project (`.forgestack.toml`), deep-merged. A project phases list **replaces** the global phases list wholesale (array deep-merge is incoherent for ordered phases) — documented behavior.

## 4. Data model

New owned section under existing `[workflow]`:

```toml
[workflow]
engine = "agtx"
research = true        # optional research lane on/off
cyclic = false         # true: review -> planning with {phase} cycle counter

[[workflow.phases]]    # ordered; keys constrained to AGTX grammar
key = "planning"
label = "Planning"
purpose = "Turn requirements into an implementation-ready contract."
agent = "codex"        # provider id from adapter registry (adapter.name)
skills = ["matt", "superpowers"]   # detected packs or forgestack sub-skills
team = ["Senior Unity3D dev", "Senior Artist", "UI expert"]  # OPT-IN, disabled by default (omit or []); penalty: extra tokens per planning run
artifact = "spec.md"   # optional: docs/<plugin-name>/<file>
prompt = ""            # empty -> default template rendered from label+purpose

[[workflow.phases]]
key = "preresearch"    # optional one-time project hook
purpose = "Introduce the repo conventions."
```

`Config` dataclass gains `phases: list[PhaseDef]`, parsed in `Config.from_dict` from `values["workflow"]["phases"]`. `PhaseDef` fields: `key, label, purpose, agent, skills: list[str], team: list[str], artifact: str | None, prompt: str`. `PhaseModel` = `list[PhaseDef]` + `research: bool` + `cyclic: bool`.

Allowed keys: `{research, planning, running, review, preresearch}`. When no `[workflow.phases]` is configured, the default model = current forgestack plugin (research + planning + running + review with default prompts). `team` is opt-in and disabled by default (omit/`[]` → standard planning prompt, no roster, no coverage matrix); it is only allowed on `planning` and is ignored with a warning elsewhere.

`render_toml` emitter extends to write `[workflow] research`, `cyclic`, and `[[workflow.phases]]` entries.

## 5. Rendering (`src/forgestack/workflow/renderer.py`)

`render_plugin_toml(model) -> str` produces a full AGTX `plugin.toml`:

- `name = "forgestack"`, `description`, `cyclic` from model.
- `[prompts.<key>]` per phase; `preresearch` emitted as `[commands]` form (one-time hook).
- Default prompt body built from `label` + `purpose` + `{task}` placeholder, following the current plugin's research/planning/running/review prompt structure.
- `[artifacts.<key>]` when `artifact` set (path `docs/<plugin-name>/<file>`).
- Skills referenced inside the rendered prompt text via a skills-recommendation paragraph (rendered from `skills` list).
- Planning prompt extended when `team` non-empty: a **multidisciplinary sprint-planning paragraph** listing roster members and instructing one explicit role pass per member — what that role must deliver, which requirements it owns, its risks, what is commonly overlooked from its perspective. Delegation note: when the running agent's CLI supports sub-agents, each role pass may be delegated to an internal specialist sub-agent; otherwise a structured reasoning pass is sufficient.
- Planning output when `team` non-empty includes a **coverage matrix** (requirements × roles) as the deliverable, surfacing gaps as "uncovered by team" — the anti-missed/overlooked mechanism. If `team` non-empty and `artifact` unset, the planning artifact defaults to `plan.md` (spec + plan + decomposition + coverage matrix); it still never implements production code.

`render_agents_config(model) -> dict[str, str]` maps `{agent_key: provider_id}` for AGTX `config.toml [agents]`, keeping only the 4 named phase keys.

## 6. Validation (`src/forgestack/workflow/validate.py`)

`validate(model, registry) -> list[CheckResult]`:

- every key in `{research, planning, running, review, preresearch}`
- keys unique
- planning + running + review present (board-reachable)
- at least one phase prompt/command contains `{task}`
- `agent` resolves against adapter registry (`adapter.name`); unresolvable → error
- unknown `skills` names → warning, not error
- `team` allowed only on `planning`; on other phases → warning + ignored
- `preresearch` (if present) has no `artifact` requirement

## 7. CLI: `forgestack phases`

New command group in `cli.py`, backed by `src/forgestack/commands/phases_cmd.py`:

1. **`phases scaffold`** — Rich interview of the shape: phase checkboxes over the 4 + preresearch, research toggle, cyclic toggle, per-phase agent (detected providers), per-phase skill packs (detected), and an **opt-in** per-planning-phase team roster (default off; presented as a question with a token-cost note; detected specialist prompts / free-text roles). Writes phase list into active config scope (global or project — chosen by flag/args). Deterministic.
2. **`phases design`** — co-design step: launches the configured agent (subprocess, like `inbox_cmd` runs AGTX) with the scaffold plus `skills/forgestack/phase-designer` guidance; agent returns `purpose`+`prompt` per phase as TOML in fenced block; parsed, validated, merged back into config. Falls back to default templates if agent unavailable or output unparseable. When a planning `team` is present, the phase-designer guidance includes per-role pass + coverage matrix generation.
3. **`phases apply`** — renders plugin + agents wiring, backs up existing files, shows diff, asks y/N, writes, validates, prints next steps.

`setup_cmd` gains a "design workflow phases?" prompt that delegates to `phases scaffold`.

New product skill `skills/forgestack/phase-designer/SKILL.md` instructs the agent how to write per-phase `purpose`/`prompt` and emit TOML.

## 8. Tests

- `tests/unit/test_phases.py` — parse/serialize; default model when unset; project override replaces phase list.
- `tests/unit/test_render.py` — golden renders: default model → frozen `plugin.toml` string; custom model → cyclic/preresearch/artifacts/skills paragraph present; team model → planning prompt contains each roster role + coverage-matrix instruction.
- `tests/unit/test_validate.py` — each rule: bad key, duplicate, missing phase, missing `{task}`, unresolvable agent, unknown-skill warning.
- `tests/unit/test_phases_cmd.py` — scaffold writes config with mocked input; apply dry-run and diff paths (no real AGTX).

## 9. Docs

`docs/phases.md` — schema reference (Section 4), wizard walkthrough (Section 7), AGTX constraint explainer (Section 2).

## 10. Non-goals

- No new AGTX lane names; Done/Backlog stay structural.
- No replacement of AGTX as workflow authority.
- No phase-model editor UI beyond the CLI wizard + agent step.
- No per-phase agent outside the 4 named keys (AGTX limitation) — the multidisciplinary **team** is simulated inside the single planning agent via role passes / agent-internal delegation, not via multiple AGTX agents on one card.
- No shipping of third-party skill content — ForgeStack references packs, never vendors them.

## 11. Acceptance criteria

- `forgestack phases scaffold` deterministically writes a valid phase model to global or project config.
- `forgestack phases design` produces per-phase content (agent-assisted) and merges valid TOML back.
- `forgestack phases apply` writes a valid AGTX `plugin.toml` (+ project/system `[agents]` wiring) with backup, diff, and y/N approval.
- Unconfigured systems fall back to the current default model.
- Planning phase with an *enabled* `team` produces a per-role coverage matrix in its output (gap detection for missed/overlooked work); plans without a `team` use the standard planning prompt and stay token-light.
- All tests pass; ruff clean; AGTX remains untouched at runtime beyond generated config.