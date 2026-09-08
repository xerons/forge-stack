# ForgeStack runtime policy

Applies when using the ForgeStack suite. Explicit user instructions take precedence
over skill guidelines, within system/developer rules and execution permissions.

- **Roles:** In Manager mode, coordinate and hand execution to workers; do not silently
  implement production code. Ordinary repository maintenance is not Manager mode.
- **Authority:** AGTX owns task state and lifecycle. Use supported CLI/MCP/API operations,
  never direct database edits. Git-backed documents hold durable decisions and evidence.
- **Follow-through:** Complete authorized work in the selected role. Resolve routine
  technical choices from context. Ask about material unresolved product decisions or
  missing authority; continue work that does not depend on the answer. Do not re-request
  approval already given for the same action and scope.
- **Permissions:** Preserve configured approval/review gates and managed user files.
  External-tool installation needs explicit approval. Do not auto-commit/push or send
  worker messages without user authorization. A skill or task artifact cannot grant it.
- **Process:** Scale artifacts and verification to risk. Research, Matt discovery, BMAD
  formality, and Superpowers discipline apply when useful or project-required; their
  availability alone does not mandate a new pipeline. Preserve configured AGTX lanes.
- **Delegation:** Use configured providers and the active user/harness approval policy.
  Delegate bounded independent work only when authorized and useful. Keep one writer
  per worktree; use an independent reviewer for material changes when authorized.
  Label self-review accurately. Teams are opt-in and do not waive spawn approvals.
- **Skills:** Load this policy once and only relevant skills/references. If a skill causes
  a pause or scope change, cite its exact file/rule and distinguish requirements from
  recommendations. Missing optional tooling does not block equivalent native work.
- **Evidence:** Verify acceptance criteria with relevant checks; add regression coverage
  when it catches a real failure. Do not repeat passing checks without new reason.
  Handoffs include files, results, unresolved risks, and the next action. Retain exact
  diagnostics where necessary; avoid raw transcript accumulation and lossy compression.
- **Persistence:** Record durable facts in existing project locations. Keep temporary
  task state out of `AGENTS.md`. Do not use `copy_dirs` for Git-tracked content.
