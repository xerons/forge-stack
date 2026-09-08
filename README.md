# ForgeStack

**Existing tools, one development workflow.**

ForgeStack is a local-first, developer-focused orchestration and integration product that unifies a curated set of external AI development tools behind one consistent CLI, configuration model, skill suite, and workflow.

ForgeStack is an opinionated integration layer over existing tools. Upstream projects remain independently owned and licensed.

ForgeStack does **not** bundle the external AI/workflow tools it integrates with. It detects and installs supported tools from their official upstream distribution methods after user approval.

## Why does it exist?

Modern AI-assisted development uses many independent tools — workflow authority, agent CLIs, skill suites, token reducers, runtimes. Remembering each one's installation, configuration, and invocation details is friction.

ForgeStack collapses that into one product surface:

```text
forgestack setup
forgestack init
forgestack manager
forgestack board
forgestack status
forgestack inbox
forgestack doctor
forgestack update
```

## What does it install?

ForgeStack itself is a thin Python CLI (`forgestack` on PATH).

Everything else is **detected, not bundled**. ForgeStack's `setup` command discovers what's already on your machine and offers to install missing pieces through their official upstream methods — with your approval. It also installs ForgeStack's own assets (the `forgestack` skill suite and AGTX plugin) — globally by default, or per-project with `--scope project`. All ForgeStack installs are hash-tracked so your edits are never silently overwritten.

## What remains external?

ForgeStack does not reimplement, vendor, or imply authorship of these upstream projects:

- **[AGTX](https://github.com/fynnfluegge/agtx)** — workflow authority (task state, Kanban lifecycle, worktrees, worker dispatch)
- **[Herdr](https://github.com/herdrdev/herdr)** — runtime workspace
- **Agent CLIs** — [Codex](https://github.com/openai/codex), [Claude Code](https://github.com/anthropics/claude-code), [OpenCode](https://github.com/anomalyco/opencode), Gemini, Antigravity, and others
- **[BMAD](https://github.com/bmad-code-org/BMAD-METHOD)** — project-scoped method tooling
- **[Matt Pocock skills](https://github.com/mattpocock/skills)** — engineering skill suite
- **[Superpowers](https://github.com/obra/superpowers)** — disciplined implementation workflow
- **[RTK](https://github.com/rtk-ai/rtk)** — token reduction

Each is represented through an adapter with detection, installation, version/compatibility checking, and configuration.

## Quick start

```bash
git clone https://github.com/xerons/forge-stack.git
cd forgestack
./install.sh
```

Then, from any Git repository:

```bash
forgestack setup     # detect + (with approval) install tools, install ForgeStack assets, write global config
forgestack setup --scope project   # install ForgeStack assets into this project
forgestack init      # validate + prepare this project
forgestack manager   # launch a persistent Manager session (Codex by default)
```

`setup` asks before installing external tools and installs ForgeStack's skills and AGTX
plugin with managed-file protection. Run it from the Git project where you will work.
Then run `init`, configure phase routing with `agents` if needed, and start the Manager.
The Manager coordinates requirements and AGTX work; implementation and review happen in
separate worker sessions. The configured `[manager] agent` defaults to `codex`; supported
interactive launchers are Codex, Gemini, OpenCode, and Herdr. A project can override the
global configuration in `.forgestack.toml`.

For a first workflow, use `forgestack phases scaffold --scope project`, optionally run
`forgestack phases design`, then run `forgestack phases apply`. Review the diff before
confirming the generated project `.agtx/plugins/forgestack/plugin.toml`. Start AGTX with
the configured project plugin, create or import a task, and let the Manager route it
through Planning, Running, and Review. Use `forgestack status` for tool detection and
`forgestack inbox` for supported pending-decision queries; failed queries are reported as
failures rather than being shown as a clean inbox.

## Architecture

```
                    FORGESTACK
                         │
            ┌────────────┴────────────┐
            │                         │
        CLI / Config              Skill Suite
            │                         │
            └────────────┬────────────┘
                         │
                     Adapters
                         │
        ┌────────────────┼────────────────┐
        │                │                │
     Workflow          Agents        Integrations
       AGTX        Codex/Claude/...  BMAD/Matt/etc.
                         │
                    Runtime / UX
                Herdr / code-server
```

The core product owns the CLI, configuration, workflow policy, adapters, skills/prompts/templates, installation coordination, and validation flows. External tools remain external, connected through stable integration boundaries.

See [`docs/architecture.md`](docs/architecture.md) for the full design.

## Core command surface

| Command | Purpose |
| --- | --- |
| `forgestack setup` | Machine/global bootstrap: discovery, install tools (with approval), install ForgeStack assets, global config (`--scope project` installs assets per-project) |
| `forgestack init` | Project bootstrap: validate Git repo, detect BMAD, verify compatibility |
| `forgestack agents` | Dynamic provider/CLI routing configuration |
| `forgestack manager` | Persistent human-facing entry point |
| `forgestack open` | Create/attach the configured workspace |
| `forgestack board` | Open or attach AGTX |
| `forgestack status` | Compact engineering-view summary |
| `forgestack inbox` | Human Inbox: decisions, blocked tasks, approvals |
| `forgestack phases` | Design and apply the workflow phase model (scaffold → design → apply) |
| `forgestack doctor` | Diagnose without mutating unless repair is approved |
| `forgestack update` | Update ForgeStack, then report external dependency updates |

## Configuration

Global: `~/.config/forgestack/config.toml`
Project: `.forgestack.toml`

Project values override global values in a deep merge. See [architecture](docs/architecture.md)
and the workflow documentation for the supported configuration surface.

## Safety model

- Never install external tools silently — approval is always required.
- Never execute arbitrary installer URLs from untrusted manifests; installer definitions are product-owned and reviewed.
- No silent privilege escalation; display command/source before running sensitive installers.
- No provider tokens in repository config; prefer upstream auth flows.
- No auto-push, no auto-commit by default, no destructive config overwrite (backup or diff first).
- Avoid direct AGTX database manipulation.

## Development

```bash
python -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest
.venv/bin/ruff check src/
```

See [CONTRIBUTING.md](CONTRIBUTING.md), [repository agent guidance](AGENTS.md), and
the [GPT-6 Astra guidance audit](docs/agent-guidance-audit.md).

## License

[MIT](LICENSE)

*ForgeStack is an opinionated integration layer over existing tools. Upstream projects remain independently owned and licensed — see their official repositories for their terms.*
