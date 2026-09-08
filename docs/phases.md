# Workflow Phases

ForgeStack owns the workflow *model*: which phases exist, what each phase does, which agent
and skill packs it uses. AGTX remains the runtime authority — ForgeStack re-renders the AGTX
plugin from your config.

## Constraints (from AGTX)

- Board lanes are fixed: `backlog → planning → running → review → done`; research is an
  optional lane; Done/Backlog structural.
- Phase keys are limited to `research, planning, running, review, preresearch`.
- Per-phase agent routing is limited to those 4 named keys.
- A phase is reachable from Backlog only if its prompt/command contains `{task}`.

## Config

```toml
[workflow]
engine = "agtx"
research = true        # optional research lane
cyclic = false         # cyclic review -> planning

[[workflow.phases]]
key = "planning"
label = "Planning"
purpose = "Turn requirements into an implementation-ready contract."   # optional
agent = "codex"        # provider id from the adapter registry
skills = ["matt", "superpowers"]   # detected packs, referenced not vendored
team = []              # OPT-IN, disabled by default: planning-only sprint-planning roster
artifact = "plan.md"   # optional: docs/<plugin-name>/<file>
prompt = ""            # empty -> default template
```

Project `.forgestack.toml` phases replace the global list wholesale. When no phases are
configured, the current default model (research + planning + running + review) is used.

## Wizard

- `forgestack phases scaffold --scope project|global` — pick phases, research/cyclic, per
  phase agent + skill packs, and (planning, opt-in) a team roster. Deterministic.
- `forgestack phases design` — an agent fills per-phase purpose/prompt (reference
  `skills/forgestack/phase-designer`). Falls back to defaults when unavailable.
- `forgestack phases apply` — validates, diffs, then (on y/N) writes the AGTX
  `plugin.toml` and prints the `[agents]` wiring for your agtx config.toml. Writes are
  manifest-protected: a `plugin.toml` you have edited since the last write is preserved, not overwritten.

## Multidisciplinary sprint-planning (planning `team`, opt-in)

When enabled, the planning agent runs one explicit role pass per team member and produces a
requirements × roles coverage matrix that flags requirements uncovered by the team — the
anti-missing/overlook mechanism. It costs extra tokens, so it is never enabled implicitly.


## Proportionate work within phases

A tiny task can keep its plan and acceptance criteria in the card. Use separate
specifications, research, and methodology packs when uncertainty or project requirements
justify them. This changes the amount of work inside the configured lanes, not AGTX's
lifecycle or approval gates. `QA/acceptance` is review activity, not an additional phase key.

Planning teams delegate only when the active user/harness policy permits it. A roster
alone does not authorize subagents. If role passes run in one agent, label that fact;
they are not independent review. Resolve BLOCKING and IMPORTANT findings before completion.

The default prompts are maintained in `src/forgestack/workflow/model.py`. After editing
those defaults, regenerate the shipped plugin from the repository root:

```sh
.venv/bin/python - <<'PYTHON'
from pathlib import Path
from forgestack.workflow.model import PhaseModel
from forgestack.workflow.renderer import render_plugin_toml
Path("agtx/plugins/forgestack/plugin.toml").write_text(
    render_plugin_toml(PhaseModel.default())
)
PYTHON
```

A regression test compares the parsed shipped and generated plugin. Custom phase
prompts still take precedence. Existing installed assets are updated only through the
normal managed-write flow; locally edited assets remain protected.

For model settings and the instruction audit, see [agent guidance audit](agent-guidance-audit.md).
