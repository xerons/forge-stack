---
name: forgestack-project-doctor
description: Diagnose why forgestack is broken or inconsistent.
---

# Project Doctor Sub-skill

Diagnose forgestack issues in a repo.

**Check:**
- Git repository
- AGTX installation and global forgestack plugin
- Current agent routing and installed CLIs
- Plugin/agent compatibility
- BMAD project setup
- Matt skills and Superpowers availability
- Token optimizer availability/integration
- `AGENTS.md` / project docs / worktree compatibility
- `.agtx` config/ignore issues

Produce a "ForgeStack Doctor" report summarizing these items and providing recommended actions. Do not mutate unless the user asks to repair.
