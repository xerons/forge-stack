---
name: forgestack-setup
description: Bootstrap project-specific forgestack requirements.
---

Read [shared policy](../POLICY.md) once per session when using this skill.

# Setup Sub-skill

**Responsibilities:**
- Verify current directory is a Git repo.
- Verify AGTX is installed.
- Verify global forgestack plugin exists.
- Invoke `agents` sub-skill if routing is missing/invalid.
- Detect Matt skills if the chosen workflow uses them.
- Check BMAD setup if formal planning is selected; install only through the supported upstream flow with explicit approval.
- Check Superpowers compatibility if selected; use equivalent native discipline if optional tooling is unavailable.
- Detect optional token optimization tooling via `token-optimizer`.
- Inspect `AGENTS.md` / docs / architecture / ADR conventions. Preserve existing project docs.
- Avoid creating `.agtx/config.toml` unless project override is needed.
- Inspect `.gitignore` safely. Do not use `copy_dirs` for tracked content.
- **Do not** blindly ignore all of `.agtx` if project config/plugins should be tracked.
- **Do not** auto-run AGTX or commit/push.

Delegate provider/CLI selection to `agents/SKILL.md`, do not hard-code routing.
Token optimizers should be detected but not enabled automatically without user approval.
