---
name: forgestack-workflow-policy
description: Choose proportionate planning, research, and review for a ForgeStack task.
---

Read [shared policy](../POLICY.md) once per session when using this skill.

# Workflow policy

Choose process by uncertainty, impact, and acceptance criteria. Preserve configured
AGTX lifecycle gates; reduce artifact size and redundant work inside those gates.

| Task | Planning and evidence |
| --- | --- |
| Tiny, familiar, low risk | Brief plan and acceptance criteria in the card; focused verification and concise review. |
| Normal change | Implementation plan, relevant regression checks, independent review when authorized. |
| Uncertain behavior or architecture | Targeted Research first; resolve the specific unknown before committing to a plan. |
| High impact or security-sensitive | Document affected boundaries and rollback where relevant; focused independent security/acceptance review. |

Research is optional. QA/acceptance is review work, not an invented AGTX phase key.
Do not create separate spec/plan files or activate every methodology for every task.
When working directly on a repository outside Manager mode, use its normal development
workflow; do not bootstrap a board solely to satisfy this skill.
