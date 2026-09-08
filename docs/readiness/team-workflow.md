# G1 readiness run: Manager → AGTX worker → review

Recorded 2026-09-07 from the isolated project
`<isolated-project-root>`.

This run exercises the ForgeStack integration without modifying the production
repository's runtime code. AGTX is authoritative for task status.

Local paths, session IDs, project IDs, and task IDs are redacted in this public copy;
the full values are retained in the disposable AGTX artifacts used for verification.

## Evidence

- **Manager session:** `forgestack manager` launched a separate interactive Codex
  session in the isolated project. The elevated launch session was `<manager-session-id>`.
  The Manager successfully called AGTX `list_projects` and reported the active
  task state. Its project root was `<isolated-project-root>`.
- **Project/plugin/provider:** AGTX project
  `<agtx-project-id>` is
  `forgestack-readiness-20260907`. Project config selects the ForgeStack plugin
  and routes all configured phases to Codex. AGTX reports version `1.0.2`.
- **Task/session:** task
  `<agtx-task-id>`, “Implement greeting function with
  clarified blank-name behavior,” uses the Codex worker session
  `<worker-session-id>`
  and worktree
  `<worker-worktree>`.
  The current AGTX state is `review`; allowed next actions are
  `move_to_done` and `resume`.
- **PO gate:** before implementation, the worker asked the required product
  question. The recorded decision in `.agtx/plan.md` is that empty and
  whitespace-only names return exactly `Hello, world!`. The PO approved the
  plan before source changes.
- **Implementation/artifact:** the worktree contains `greeting.py`,
  `test_greeting.py`, `.agtx/plan.md`, and `.agtx/execute.md`. The handoff
  records the changed files, contract, test output, controlled recovery, and
  review result.
- **Controlled failure/recovery:** the deliberately missing selector was run
  with the Python 3.11 path selector and returned exit code 4. The recovery
  command
  `PATH=<python3.11-bin>:<python3.11-prefix>:$PATH python -m pytest -q`
  returned exit code 0 with `3 passed in 0.00s`. `git diff --check` returned
  exit code 0.
- **Independent review:** a separate correctness review inspected the source
  diff, contract, and fresh test output. Final verdict was
  **APPROVED / READY**, with no BLOCKING or IMPORTANT findings.
- **Regression evidence:** after the readiness documentation update, the fresh
  root commands completed successfully: `./.venv/bin/pytest -q` → `74 passed in
  0.45s`; `./.venv/bin/ruff check src/ tests/` → `All checks passed!`; and
  `git diff --check` → exit code 0.

## G1 checklist

- [x] Manager persistent and separate from workers.
- [x] Real task/provider/plugin/session evidence.
- [x] PO clarification and approved-plan gate exercised.
- [x] Approved artifact received; implementation tests ran.
- [x] Independent review complete; important findings resolved.
- [x] Failure visible and recovery demonstrated.
- [ ] Actual PO acceptance recorded.
- [x] Regression checks and required reviews passed after this documentation update.

**Current verdict: PENDING PO ACCEPTANCE.** The implementation and review gates
are complete, but the task must remain in AGTX `review` until the Product
Owner explicitly accepts the result. After acceptance, run the final regression
commands, record their fresh output here, and call AGTX `move_to_done`.
