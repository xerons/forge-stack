---
name: forgestack-project-doctor
description: Diagnose why forgestack is broken or inconsistent.
---

Read [shared policy](../POLICY.md) once per session when using this skill.

# Project Doctor Sub-skill

Diagnose forgestack issues in a repo.

**Check the areas relevant to the symptom; for a full health check, cover:**
- Git repository
- AGTX installation and global forgestack plugin
- Current agent routing and installed CLIs
- Plugin/agent compatibility
- BMAD project setup
- Matt skills and Superpowers availability
- Token optimizer availability/integration
- `AGENTS.md` / project docs / worktree compatibility
- `.agtx` config/ignore issues

Produce a "ForgeStack Doctor" report summarizing these items and providing recommended actions. For a diagnostic request, report findings. If the user already requested repair, complete scoped reversible fixes without asking again; preserve installation and destructive-action approvals. Missing optional tools are informational unless the selected workflow requires them.
