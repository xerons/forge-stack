---
name: forgestack-agtx-control
description: Safely operate AGTX using supported CLI/MCP/API.
---

Read [shared policy](../POLICY.md) once per session when using this skill.

# AGTX Control Sub-skill

Safely operate AGTX using supported interfaces (CLI, MCP, API).

**Capabilities:** List tasks, inspect task/phase, move task, start phase, read worker pane/status, send message to worker, inspect blockers/dependencies, stop/resume, create/update task (if supported).

**Rules:**
- **Never modify internal AGTX DB directly.**
- If create/update is not exposed, report limitation. Thin wrappers are acceptable only around supported behavior.
- Confirm destructive actions. Do not skip approval/review gates unless explicitly enabled.
- Use dynamically configured agent routing.
- Retrieve only task/pane data needed for the operation (avoid ingesting entire board logs).
- Route confirmed BLOCKING or IMPORTANT findings to the responsible phase for correction through supported lifecycle transitions; do not declare completion with unresolved material findings.
