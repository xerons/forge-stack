---
name: forgestack-agents
description: Discover available coding-agent CLIs and configure AGTX routing.
---

# Agents Sub-skill (Dynamic CLI Routing)

Discover available coding-agent CLIs and configure AGTX routing interactively. **Do NOT hard-code a fixed stack.**

## 1. Discover Available Agents
Inspect the local machine for: `codex`, `agy` (AGTX id: `antigravity`), `claude`, `gemini`, `opencode`, `cursor-agent`, `copilot`, etc.
Build an inventory with display name, AGTX id, executable, version, availability, and compatibility notes.

## 2. Ask User for Routing
Ask the user which agent should handle: **Research**, **Planning**, **Running**, **Review**.
Research is optional. Allow the same agent in multiple phases.

## 3. Recommendation Mode
If asked to recommend:
- Research: exploration / large-context capability.
- Planning: strongest reasoning.
- Running: efficient coding worker.
- Review: strong independent reasoning (ideally different from Running).

## 4. Scope
Ask if routing should be Global (`~/.config/agtx/config.toml`) or Project-only (`<repo>/.agtx/config.toml`).

## 5. Config Writing
Generate config block and ask which is `default_agent`. Show proposed changes before writing. Do not invent a fallback Research worker if disabled.

## 6. Validate
Verify executable exists, AGTX identifier is valid, plugin supports agents, phase compatibility, and token-optimizer compatibility.
If `supported_agents` in plugin restricts choice, warn and offer to update it.

## 7. Reconfiguration
Support showing current routing, changing single phases, resetting to global, adding new CLIs.
