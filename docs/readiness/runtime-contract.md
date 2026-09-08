# ForgeStack readiness runtime contract

Recorded 2026-09-07 while preparing the isolated G1 readiness story. Versions and
limitations below are observed on the local machine; they are not assumed to apply to
other installations.

The public copy intentionally redacts local filesystem paths and disposable session or
project identifiers. The corresponding full identifiers remain in the local AGTX task
artifacts used for verification.

## Installed components

| Component | Version/path | Result |
| --- | --- | --- |
| ForgeStack | repository `8f9687f` plus current uncommitted changes | Python tests and Ruff pass. |
| AGTX | `1.0.2`, `agtx` | Installed; MCP control surface is available to the Codex session. Terminal startup cannot run in this sandbox because AGTX's logger/TUI requires external device/config access. |
| Herdr | `0.8.2`, `herdr` | Installed; `default` session exists but is stopped. `herdr --help` and `herdr --skill` were readable. Control commands require `HERDR_ENV=1` inside a Herdr-managed pane. |
| Codex | `codex-cli 0.153.4`, `codex` | Installed. `codex exec` supports `-C/--cd`, a positional initial prompt, and resume subcommands. |
| Gemini | installed at `gemini` | Help confirms `--prompt-interactive`. |
| OpenCode | installed at `opencode` | Help confirms project positional argument and `--prompt`. |
| AGY | installed at `agy` | Help exposes interactive prompt options, but ForgeStack does not assume it for Manager launch. |

## Verified ForgeStack launch contract

The Manager reads the project config and loads the product Manager skill. With
`[manager] agent = "codex"`, it launches:

```text
codex -C <git-project-root> <manager-instructions>
```

The process stays interactive and receives the project root as its working directory.
The Manager is therefore a separate session from AGTX delivery workers. The current
implementation also supports these verified launcher shapes:

```text
gemini --prompt-interactive <manager-instructions>
opencode <git-project-root> --prompt <manager-instructions>
herdr --session forgestack-manager
```

The Herdr launcher attaches a persistent workspace; it does not silently invent an
agent or permissions. If Herdr is used, start the configured worker through Herdr's
supported agent surface. Unsupported providers return an error instead of falling back
to an unverified command.

The launch contract was exercised in the disposable project
`<isolated-project-root>` with the configured Codex provider. The
Manager ran as session `<manager-session-id>`, used the isolated project as its root, and called the
AGTX MCP `list_projects` operation. It reported the active AGTX task rather than
starting a second worker or editing production code. The TUI needed an elevated
interactive launch on this machine; the first sandboxed attempt failed because the
Codex state database was read-only.

## AGTX control contract

AGTX's terminal binary reports version `1.0.2`. Its CLI startup attempted to initialize
the rolling logger and failed in this non-interactive sandbox with a device/config
permission error, so no TUI task transitions were guessed or fabricated. AGTX exposes
the following MCP operations to the active Codex session and they are the supported
read/write control surface used for readiness:

- `list_projects`, `list_tasks`, `get_task`, `create_task`, `update_task`
- `move_task`, `get_transition_status`, `read_pane_content`, `send_to_task`
- `get_notifications`, `check_conflicts`

Always call `list_projects` first and pass the returned project ID to later operations.
Observe the task's allowed actions before moving it. AGTX remains authoritative for task
state, worker lifecycle, and phase transitions. Direct database edits are unsupported.

The installed global AGTX config currently routes research/planning/review to `codex`
and running to `antigravity`; a demo project should use a project-scoped config and
explicitly verify effective routing before starting a worker.

The project-scoped readiness config selected the `forgestack` plugin and routed each
configured phase to Codex. AGTX then created task
`<agtx-task-id>` with a distinct worker session and worktree.
The task reached `review` with `move_to_done` available after the worker handoff and
independent review. This is the observed create → plan → run → review path; the final
transition remains gated on explicit PO acceptance.

## ForgeStack phase and inbox contracts

- `forgestack phases scaffold --scope project` writes the project phase model.
- `forgestack phases design --scope project` may ask the selected agent to fill prompts;
  timeout and nonzero exits are rejected without overwriting the config.
- `forgestack phases apply --scope project` validates and parses the generated plugin
  before the managed write, prints the diff, and asks for confirmation.
- Generated TOML uses escaped basic strings and is parsed before writes, preserving
  quotes, backslashes, newlines, tabs, and other control characters.
- The optional research flag controls rendering; a flag/list mismatch is reported as a
  warning rather than silently changing the user's configuration.
- `forgestack inbox` uses the legacy CLI query when available. A nonzero query is shown
  as a failure; it is never reported as “Inbox clean”. In Codex, use AGTX MCP task
  queries for the authoritative decision state.

## Readiness verdict

The local unit and lint checks prove ForgeStack's command and serialization behavior.
The isolated G1 run in `team-workflow.md` now records actual task IDs, provider/session
evidence, the clarification gate, worker output, independent review, and failure/recovery.
G1 remains pending only the explicit PO acceptance; AGTX must stay in `review` until that
response is recorded.
