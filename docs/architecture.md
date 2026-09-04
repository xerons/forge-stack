# ForgeStack Architecture

ForgeStack is a thin, opinionated **integration/orchestration layer** over external upstream tools. It owns a CLI, a unified config, adapters, product-owned skills, an AGTX plugin, workflow policy, and doctor/setup/update logic. It deliberately does not implement the capabilities of upstream tools.

## Layers

```text
              CLI (typer)
                │
   unified config ──────────► adapters
        ▲                        │
        │          ┌─────────────┼────────────────┐
   profile/merge   │            │                │
        │        Workflow      Agents       Integrations
        │         AGTX     codex/claude/   bmad/matt/sp/rtk/
        │                  opencode/agy   herdr/code-server
        │                        │
        └─────────────── Runtime/UX (herdr)
```

## Module map

- `forgestack/cli.py` — Typer root app. Commands are thin wrappers over `commands/*`.
- `forgestack/config.py` — global/project TOML load + deep merge; tiny writer for owned keys.
- `forgestack/paths.py` — global/project path resolution.
- `forgestack/managed.py` — managed-file ownership manifest: hash-tracked writes per install root with atomic save. `check()` returns `ABSENT/SAFE/MODIFIED/FOREIGN`; `write_managed()` writes only `ABSENT/SAFE` files and preserves `MODIFIED`/`FOREIGN`. Manifest lives at `<root>/.forgestack-managed.json`.
- `forgestack/assets.py` — locates product-owned installable assets in the source tree (`skills/forgestack/`, `agtx/plugins/forgestack/plugin.toml`).
- `forgestack/adapters/protocol.py` — the single adapter Protocol each tool implements.
- `forgestack/adapters/registry.py` — manifest-driven list of adapters by category.
- `forgestack/commands/` — one module per command. `setup` detects + installs ForgeStack assets; `phases` and `agents` write config/plugin through `write_managed`.
- `forgestack/workflow/` — AGTX phase model, config parsing, validation, and plugin render.
- `skills/forgestack/` — product-owned skill suite (migrated from scrum-stack prototype).
- `agtx/plugins/forgestack/plugin.toml` — ForgeStack-owned AGTX plugin (installed from source via `assets.py`).
- `manifests/tools.toml` + `manifests/compatibility.toml` — data-driven tools/version policy (planned: consumed by future install/update stages; not yet read at runtime).

## Managed-file ownership

Files ForgeStack writes are tracked in a per-install-root manifest (`.forgestack-managed.json`) so updates never overwrite user edits. When a write is attempted:

- file absent from disk or unchanged since install → **written** (hash recorded/updated)
- tracked file the user edited (hash differs) → **preserved** + warning
- untracked, non-empty file at the target path (foreign) → **never overwritten** + warning

The manifest is a single JSON file per install root; keys are paths relative to that root. This protects `setup` asset installs, `phases apply`, and `agents` writes.

## Style-ish rules

- Thin wrappers; upstream does the heavy lifting.
- Adapters never vendored. Install only after `y/N` approval with commands displayed.
- All state that upstream owns (AGTX, herdr, skills dirs) is invoked via CLI/API, never DB manipulation.
