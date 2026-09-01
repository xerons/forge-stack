# ADR-0001: Implementation language and runtime

## Status

Accepted

## Context

ForgeStack needs a CLI-first user experience with rich terminal output, a small
typed domain model, easy subprocess calling for adapters, and a small test
footprint. The product spec prefers Python 3.11+. TypeScript was offered as an
alternative only with strong reason; none applies.

## Decision

- **Language/runtime:** Python 3.11+
- **CLI framework:** Typer
- **Terminal UI:** Rich
- **TOML:** stdlib `tomllib` for reading; minimal internal emitter for writing
  known keys (no new dependency)

## Consequences

- Easy subprocess/orchestration, and extraction for the adapter registry.
- `pyproject.toml` declares console script `forgestack`.
- If a second runtime is ever needed, ADR required.
