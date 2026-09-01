---
name: forgestack-setup
description: Bootstrap project-specific forgestack requirements.
---

# Setup Sub-skill

**Responsibilities:**
- Verify current directory is a Git repo.
- Verify AGTX is installed.
- Verify global forgestack plugin exists.
- Invoke `agents` sub-skill if routing is missing/invalid.
- Verify Matt skills availability.
- Verify BMAD project setup (run `npx bmad-method install` interactively if missing and user approves).
- Verify Superpowers availability separately from compatibility.
- Detect optional token optimization tooling via `token-optimizer`.
- Inspect `AGENTS.md` / docs / architecture / ADR conventions. Preserve existing project docs.
- Avoid creating `.agtx/config.toml` unless project override is needed.
- Inspect `.gitignore` safely. Do not use `copy_dirs` for tracked content.
- **Do not** blindly ignore all of `.agtx` if project config/plugins should be tracked.
- **Do not** auto-run AGTX or commit/push.

Delegate provider/CLI selection to `agents/SKILL.md`, do not hard-code routing.
Token optimizers should be detected but not enabled automatically without user approval.
