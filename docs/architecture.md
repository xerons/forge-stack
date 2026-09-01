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
- `forgestack/adapters/protocol.py` — the single adapter Protocol each tool implements.
- `forgestack/adapters/registry.py` — manifest-driven list of adapters by category.
- `forgestack/installers/` — brew / npm / pipx / curl-script / manual backends. Install plans are generated, displayed, approved (`y/N`), then executed.
- `forgestack/workflow/` — AGTX routing mapping and render.
- `forgestack/doctor/` — validation checks across config/adapters/plugin.
- `forgestack/manager/` — thin wrappers invoking herdr/AGTX.
- `skills/forgestack/` — product-owned skill suite (migrated from scrum-stack prototype).
- `agtx/plugins/forgestack/plugin.toml` — ForgeStack-owned AGTX plugin.
- `manifests/tools.toml` + `manifests/compatibility.toml` — data-driven tools and version policy.

## Style-ish rules

- Thin wrappers; upstream does the heavy lifting.
- Adapters never vendored. Install only after `y/N` approval with commands displayed.
- All state that upstream owns (AGTX, herdr, skills dirs) is invoked via CLI/API, never DB manipulation.
