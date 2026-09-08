---
name: forgestack-agents
description: Discover coding-agent CLIs and configure ForgeStack/AGTX phase routing when routing is requested or invalid.
---

Read [shared policy](../POLICY.md) once per session when using this skill.

# Agents Sub-skill (Dynamic CLI Routing)

Discover available coding-agent CLIs and configure AGTX routing interactively. **Do NOT hard-code a fixed stack.**

## 1. Discover Available Agents
Inspect the local machine for: `codex`, `agy` (AGTX id: `antigravity`), `claude`, `gemini`, `opencode`, `cursor-agent`, `copilot`, etc.
Build an inventory with display name, AGTX id, executable, version, availability, and compatibility notes.

## 2. Ask User for Routing
Reuse valid routing and explicit user choices. Ask only for missing selections for: **Research**, **Planning**, **Running**, **Review**.
Research is optional. Allow the same agent in multiple phases.

## 3. Recommendation Mode
If asked to recommend:
- Research: exploration / large-context capability.
- Planning: strongest reasoning.
- Running: efficient coding worker.
- Review: strong independent reasoning (ideally different from Running).

## 4. Scope
Preserve the requested or existing scope; when a new scope is unspecified, use Project-only. Global changes require explicit authorization. Available scopes are Global (`~/.config/agtx/config.toml`) or Project-only (`<repo>/.agtx/config.toml`).

## 5. Config Writing
Generate only the requested config changes. Reuse `default_agent` when valid; ask if a required choice remains unresolved. Show the diff and honor the command's write confirmation. Do not invent a fallback Research worker if disabled.

## 6. Validate
Verify executable exists, AGTX identifier is valid, plugin supports agents, phase compatibility, and token-optimizer compatibility if an optimizer is selected.
If `supported_agents` restricts choice, explain the compatibility constraint; do not bypass it.

AGTX agent identifiers select CLIs, not model IDs. Configure models/reasoning through
the selected CLI's supported settings, preserving explicit user choices. Verify current
official documentation for model-specific changes. Do not force every phase onto a
flagship model or assume maximum reasoning is optimal; compare representative tasks.
A routing request does not launch workers or authorize additional subagents.

## 7. Reconfiguration
Support showing current routing, changing single phases, resetting to global, adding new CLIs.
