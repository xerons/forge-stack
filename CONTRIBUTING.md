# Contributing

Thanks for considering a contribution to ForgeStack.

## Ground rules

- ForgeStack is an **integration layer**. Do not vendor, fork, or copy upstream tool source or binaries into this repository.
- External tools are detected and installed through their official upstream methods — never bundled.
- Keep the core thin: CLI, config, adapters, skills, docs, and tests. When in doubt, prefer an adapter over a hard-coded integration.

## Setup

```bash
python -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

## Verification

```bash
.venv/bin/ruff check src/
.venv/bin/pytest
```

Run both before pushing. CI runs the same commands.

## Project layout

- `src/forgestack/` — CLI, config, adapters, paths.
- `skills/forgestack/` — ForgeStack skill suite.
- `agtx/plugins/forgestack/` — AGTX workflow plugin.
- `manifests/` — tool and compatibility manifests.
- `docs/` — architecture and decision records.
- `tests/` — unit, integration, smoke.

## Adding an external-tool adapter

1. Add the tool to `manifests/tools.toml`.
2. Create `src/forgestack/adapters/<name>.py` implementing the `Adapter` protocol in `src/forgestack/adapters/protocol.py`.
3. Register it in `src/forgestack/adapters/registry.py`.
4. Add a unit test under `tests/unit/`.
5. Document it in `docs/`.

## Commits

Use [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, `test:`, `chore:`, ...).

## Licensing

By contributing, you agree your contributions are licensed under the [MIT License](LICENSE). Upstream projects integrated by ForgeStack remain governed by their own licenses.