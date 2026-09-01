# Shared Policy

- **Manager coordinates.** The Manager must not silently implement production code or become the source of truth for task/project state.
- **AGTX is authoritative.** It holds task state and lifecycle. Use AGTX CLI/MCP/API instead of direct DB mutations.
- **Workers execute.** They execute phase-specific work and must not invent unresolved product decisions.
- **Important decisions** must be written to Git-backed docs or AGTX artifacts. Git is the shared source of truth.
- **Research is optional.**
- **Matt Pocock skills** are the default for Manager-side discovery when useful, and optional specialist skills inside AGTX.
- **BMAD** is the formal planning/architecture/acceptance/QA methodology.
- **Superpowers** is for implementation discipline where available and compatible. Otherwise, require equivalent discipline (plan/test/verify/self-review).
- **Agent routing** is dynamic and user-configurable. Do not assume a specific CLI/provider.
- **Do not auto-commit or auto-push.**
- **Do not use `copy_dirs` for content already tracked by Git.**
- **Escalate genuine human/product decisions** instead of guessing.
- **Review should be independent** from implementation when practical.
- **Preserve existing project conventions** rather than imposing redundant structures.
- **Context Management:** Load only the minimum context necessary. Prefer summaries over full transcripts.
- **Token optimization** is opportunistic. Correctness, evidence, and debuggability always take priority over token savings. Do not blindly stack aggressive compression layers.
