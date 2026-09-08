# Working on ForgeStack

ForgeStack is a Python 3.11+ CLI and integration layer. Keep upstream tools external;
use adapters and supported CLIs/APIs rather than copying their implementations.

## Scope and execution

- A request to change this repository authorizes scoped implementation and verification.
  Work through completion; resolve routine choices from code and existing conventions.
- The Manager-only role applies when operating a ForgeStack-managed project as its
  Manager. It does not prevent a coding session from maintaining this repository.
- Follow system/developer instructions and explicit user direction. Skills guide the
  task; they do not grant permissions or override the user's requirements. If a skill
  blocks authorized work, identify its file and exact rule, and continue independent work.
- Inspect `git status --short` before editing and preserve unrelated user changes.
  Do not commit, push, install external tools, or operate a live board without authorization.
- Ask only for missing decisions that materially affect scope, correctness, or authority.
  Preserve accepted decisions when the user steers the task; continue unaffected work.

## Navigation and conventions

- `src/forgestack/commands/`: Typer commands; keep command handlers thin.
- `src/forgestack/adapters/`: upstream integrations and detection.
- `src/forgestack/workflow/`: phase model, validation, and AGTX rendering.
- `skills/forgestack/`: installable skills; read only the selected skill and relevant
  references. Shared runtime policy lives in `skills/forgestack/POLICY.md`.
- `agtx/plugins/forgestack/plugin.toml`: shipped default plugin; keep its parsed content
  synchronized with `render_plugin_toml(PhaseModel.default())`.
- `tests/`, `CONTRIBUTING.md`, `docs/architecture.md`, `docs/phases.md`: validation and design.

Use `rg` to narrow reads. Parallelize independent read-only commands when useful;
keep writes and dependent operations sequential. Preserve managed-file ownership,
user configuration, AGTX phase grammar, and provider-neutral routing.

## Delegation and evidence

Handle localized work directly. For independent investigations or material reviews,
follow the user's agent/model approval policy before spawning. Use bounded assignments,
one writer per working tree, and fresh review evidence; do not treat a role-playing pass
as independent review. A configured planning team does not itself authorize spawning.

Run checks appropriate to the change. Existing repository checks are:

```sh
.venv/bin/ruff check src/
.venv/bin/pytest tests/ -q
```

Use targeted tests while iterating; run the checks above before completing Python or
workflow-prompt changes. For documentation-only edits, check links and skill metadata.
Add tests for meaningful behavioral contracts, not wording or headings. Repeat or broaden
checks only for changed code, failures, or unresolved risk. Never imply an unrun check passed.

Report the outcome, changed files, actual validation, and remaining limitations concisely.
For model tuning and the rationale behind this guidance, read
`docs/agent-guidance-audit.md` only when relevant.
