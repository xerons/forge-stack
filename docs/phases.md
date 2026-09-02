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
- `forgestack phases apply` — validates, backs up, diffs, then (on y/N) writes the AGTX
  `plugin.toml` and prints the `[agents]` wiring for your agtx config.toml.

## Multidisciplinary sprint-planning (planning `team`, opt-in)

When enabled, the planning agent runs one explicit role pass per team member and produces a
requirements × roles coverage matrix that flags requirements uncovered by the team — the
anti-missing/overlook mechanism. It costs extra tokens, so it is never enabled implicitly.
