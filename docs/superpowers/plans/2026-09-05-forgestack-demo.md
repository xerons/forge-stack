# ForgeStack AI Team Portfolio Demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Use superpowers:subagent-driven-development only after applicable agent/model/assignment approval. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Verify ForgeStack can coordinate an AI team with the user as PO, use that team to deliver a game prototype, and optionally demonstrate a live update.

**Architecture:** ForgeStack owns configuration, manager initialization, skills, and integration behavior. AGTX owns task/worker lifecycle; Codex provides a persistent manager and distinct delivery/review sessions. Prove the integration in an isolated project before using it in the demo repository.

**Tech Stack:** Existing Python/Typer application and pytest suite; installed AGTX and Codex; optional Herdr workspace; Phaser 3 and a local static server.

**Spec:** [AI Team Portfolio Demo — Design](../specs/2026-09-05-forgestack-demo-design.md)

## Global Constraints

- **G2 is sufficient for a complete portfolio demo. No live update is required.**
- AGTX remains authoritative for task state.
- One writer per shared working tree.
- Use installed help/source and bounded probes; do not guess CLI syntax.
- Production implementation must come from the worker workflow.
- This documentation revision does not authorize implementation, external publication, worker spawning, or committing user changes.

Inspect applicable instructions and worktree state before execution. Obtain required approval before spawning proposed agents. Material implementation requires independent review; security-sensitive changes require security review under applicable policy. Stage/commit only selected files when authorized. This plan does not bypass those gates.

## File and responsibility map

`FORGESTACK` = this repository:

| Files | Responsibility |
| --- | --- |
| `docs/readiness/runtime-contract.md` (new) | Verified versions, operations, exact commands, limitations |
| `docs/readiness/team-workflow.md` (new) | G1 runbook and actual evidence |
| `src/forgestack/workflow/renderer.py`, `validate.py`; `src/forgestack/config.py`; `src/forgestack/commands/phases_cmd.py` | Configuration/rendering hardening |
| `src/forgestack/commands/manager_cmd.py` | Initialize configured persistent manager |
| `src/forgestack/commands/inbox_cmd.py` | Truthful decision/query outcomes |
| `skills/forgestack/manager/SKILL.md`, `agtx-control/SKILL.md`, `human-inbox/SKILL.md`, `artifact-handoff/SKILL.md` | Verified coordination procedure |
| `tests/unit/test_render.py`, `test_config.py`, `test_phases_cmd.py`, `test_validate.py` | Existing regression suites to extend |
| `tests/unit/test_manager_cmd.py`, `tests/unit/test_inbox_cmd.py` (new) | Launch and failure regressions |
| `README.md`, `docs/phases.md` | Actual setup/routing/launch behavior |

Task 1 resolves exact upstream interfaces and any additional implementation files before dependent code work. Do not invent integrations to satisfy the table.

`DEMO` = proposed sibling `<sibling-demo-project>`:

- Project configuration, generated plugin/manifest, verified AGTX routing/activation.
- `game-source/main.js`, `vendor/phaser.min.js`, license/provenance, `run-game.html`, `run-game.sh`.
- Product brief, backlog, decisions, phase artifacts under `docs/ai/`.
- Verification, case study, decision log, portfolio summary, `recordings/README.md` and media.
- Optional update story and update-specific evidence.

## Phase 1 — Fix and verify ForgeStack

### Task 1: Verify the installed runtime contract

**Files:** Create `docs/readiness/runtime-contract.md`.
**Interfaces:** Consumes installed help/source and existing commands/adapters. Produces verified invocations/configuration/evidence mappings for Tasks 3–5.

- [x] Read manager, board, inbox, phases commands; AGTX/Herdr adapters; installed tool instructions; manager/control/handoff skills.
- [x] Locate installed binaries and versions using bounded read-only commands. Use PTY only where required; stop hung probes. Do not start exploratory manager loops in the product repository.
- [x] Record actual supported syntax, results, and limitations for every row:

| Operation | Version | Invocation/configuration | Observed result | Limitation |
| --- | --- | --- | --- | --- |
| Persistent manager with initial instructions | Codex 0.153.4 | `forgestack manager` in isolated project | Manager session `<manager-session-id>` called AGTX MCP and reported task state | TUI required elevated interactive launch on this machine |
| Plugin activation/effective provider routing | AGTX 1.0.2 | Project `.agtx/config.toml`, ForgeStack plugin, Codex phase agents | Task used `forgestack` plugin and Codex worker | Global config differs; project scope is required |
| Create/read/update task | AGTX 1.0.2 | AGTX MCP after `list_projects` | Task `<agtx-task-id>` created/read | AGTX remains authoritative |
| Start phase; inspect worker/state | AGTX 1.0.2 | `move_task`, `get_task`, transition status | Worker session/worktree reached `review` | TUI side effects require active AGTX |
| Artifact handoff | ForgeStack/AGTX | `.agtx/plan.md`, `.agtx/execute.md` | PO decision, diff, tests, and handoff recorded | Handoff is in disposable worktree |
| Question, PO answer, continuation | ForgeStack/AGTX | Manager/worker question gate | Blank-name contract recorded before implementation | Final PO acceptance is still pending |
| Independent review/rework | Codex review session | Separate review of diff and test output | APPROVED / READY; no BLOCKING or IMPORTANT findings | Review evidence is recorded outside AGTX review.md |
| PO acceptance recording | AGTX gate | `move_to_done` after PO response | Not yet recorded; task remains `review` | This is the remaining G1 gate |

- [x] Choose the supported manager launch: direct interactive Codex or Herdr configured to start that session. Record exact argv, working directory, instruction loading, and resume behavior.
- [ ] Identify supported blocked/question statuses and answer-routing procedure, including any supported UI boundary. Verify the manager can operate required steps using available tools.
- [x] Produce verdict: supported with the documented project-scoped configuration and elevated interactive launch limitation. No one-prompt `drive_story.py` fallback was used.

Task 1 is a discovery gate, not G1. Task 2's independent hardening can proceed if upstream integration is blocked.

### Task 2: Harden phase configuration and serialization

**Files:** Renderer, validate, config, phases command, and existing associated tests.
**Interfaces:** Preserve `render_plugin_toml(model) -> str`, `render_toml(config) -> str`, and validation conventions. Generated output must parse and preserve strings before writes.

- [x] Add cases for research enabled/disabled, warning on mismatched flag/list, prompt/purpose round trips with quotes/backslashes/newlines/control characters, and refused writes preserving the old file. Example:

```python
def test_prompt_round_trip():
    import tomllib
    from forgestack.workflow.model import PhaseModel
    from forgestack.workflow.renderer import render_plugin_toml

    model = PhaseModel.default()
    text = 'Task:\n{task}\nUse """quoted""" text and C:\\temp.\tEnd.'
    next(p for p in model.phases if p.key == "running").prompt = text
    assert tomllib.loads(render_plugin_toml(model))["prompts"]["running"] == text
```

- [x] Run `.venv/bin/pytest tests/unit/test_render.py tests/unit/test_config.py tests/unit/test_phases_cmd.py tests/unit/test_validate.py -q`; record actual failures.
- [x] Skip research rendering when disabled and warn on mismatch. Serialize affected TOML strings safely; verify round trips including control characters. Parse entire generated documents before managed/direct writes. Failure leaves existing files intact and never reports successful writes. Preserve unrelated configuration and managed-file protection.
- [x] Correct phase-design timeout handling to catch `subprocess.TimeoutExpired`; reject failed agent executions before merging their output. Add mocked timeout/nonzero-result regressions.
- [x] Run targeted tests, then `.venv/bin/pytest tests/ -q` and `.venv/bin/ruff check src/ tests/`. Record actual results without predicting test counts. Prepare a scoped commit after required review, when authorized.

### Task 3: Initialize a real persistent manager

**Files:** Manager command, manager skill, README; new `tests/unit/test_manager_cmd.py`. Any helper must first be named in Task 1's resolved contract.
**Interfaces:** Consumes `load_config(root).manager_agent`, project root, manager instructions, verified interactive launcher. Produces manager session separate from delivery workers.

- [x] Mock the verified launcher to test configured provider selection, project working directory, instruction loading, missing/unsupported providers, nonzero launch outcome, and absent project root. Assert the actual argv from Task 1, not guessed flags.
- [x] Run `.venv/bin/pytest tests/unit/test_manager_cmd.py -q` and record failing behavior.
- [x] Implement the verified launch path using existing manager/control/handoff policy and product-decision boundaries. Preserve interactive input/output and upstream authentication. Bare workspace launch or a one-shot implementation prompt cannot satisfy the manager contract.
- [x] Document setup, launch/resume, role boundaries, and honest Herdr fallback behavior.
- [x] Run launch regressions. After required runtime/spawn approval, check startup in the isolated readiness project: manager receives the PO brief and can inspect real supported task state. Save session evidence; G1 remains pending.

### Task 4: Verify routing, decisions, and handoffs

**Files:** Inbox command/tests; coordination skills; phases documentation/runtime contract. Change phase application only if Task 1 proves a required integration correction.
**Interfaces:** Consumes plugin, actual AGTX responses/configuration, manager session, approved artifacts. Produces effective routing and a tested decision/handoff procedure.

- [x] Add inbox tests with mocked `subprocess.CompletedProcess`: failed query/stderr reports failure; successful empty query may report clean; populated success shows decisions; timeout/missing tool reports unavailable. Failed queries must never print “Inbox clean”.
- [x] Run `.venv/bin/pytest tests/unit/test_inbox_cmd.py -q` and record failures.
- [x] Implement truthful outcomes using Task 1's supported query. Cover blocked/waiting decisions through verified queries or the manager's documented workflow. Do not invent statuses or silently claim unsupported categories are covered.
- [x] Apply test phases and activate/install routing using the exact supported procedure. Document manual setup when needed. Observe effective provider/plugin on a real worker rather than treating TOML output as proof.
- [x] Update coordination skills with verified steps: manager records PO answer, updates authoritative task/artifact, resumes the correct worker; implementation receives approved plan; review receives spec/diff/tests/handoff; important findings return to implementation; final acceptance comes from PO.
- [x] Demonstrate progress via real task state and manager reports. Keep `forgestack status` labeled as tool detection unless new task-progress behavior is deliberately implemented and tested.
- [x] Run focused and full suite/lint after changes. Complete required independent correctness/security reviews and resolve material findings before G1.

### Task 5: Execute the readiness story — G1

**Files:** New `docs/readiness/team-workflow.md`; disposable project containing `greeting.py`, tests, and artifacts.
**Interfaces:** Consumes Tasks 1–4 and spec §6. Produces real G1 verdict and evidence.

The committed readiness summary redacts disposable local paths and session/project/task
identifiers; complete values remain in the local AGTX artifacts used during verification.

- [x] Create an isolated directory with `mktemp -d`, initialize Git, and configure it with the verified project-scope procedure. Record path/versions.
- [x] Launch manager and submit the spec's greeting brief. Manager asks the real PO about blank-name behavior; record answer and approved plan. Wait for required decisions and worker authorization.
- [x] Manager starts the implementation worker through supported task operations. Capture task/session identity, approved artifact handoff, actual test results, and diff. Verify unresolved product questions prevent implementation.
- [ ] Start independent review in a separate session. Save findings, correct important findings and re-review when necessary. Request actual PO acceptance and record response.
- [x] Exercise controlled blocking/failure in the isolated project and demonstrate visible failure and recovery. Use a fixture or supported control; do not revoke real credentials or affect unrelated processes.
- [ ] Complete G1 evidence:

```markdown
- [x] Manager persistent and separate from workers
- [x] Real task/provider/plugin/session evidence
- [x] PO clarification and approved-plan gate exercised
- [x] Approved artifact received; implementation tests ran
- [x] Independent review complete; important findings resolved
- [x] Failure visible and recovery demonstrated
- [ ] Actual PO acceptance recorded
- [x] Regression checks and required reviews passed
G1 verdict: record PASS or BLOCKED with evidence and limitations.
```

Do not start Phase 2 while G1 is incomplete. Report any failed requirement and concrete corrective scope.

## Phase 2 — Produce the prototype with ForgeStack + Codex

### Task 6: Prepare the product and team workspace

**Files:** DEMO project configuration, README, vendor assets, brief/backlog/decisions, phase artifacts.
**Interfaces:** Consumes verified G1 runbook. Produces configured workspace and PO-approved game backlog.

- [ ] Inspect proposed demo path and preserve existing work. Obtain filesystem access if required; establish a separate Git root.
- [ ] Run verified project setup/scaffold/design/apply and routing/activation procedure. Check TOML parsing and effective runtime routing. Resolve managed-file conflicts explicitly.
- [ ] Verify selected game skills exist and support the pinned Phaser 3 version. Record actual paths and compatibility. Resolve or explicitly omit incompatible/missing skills with justified prompt adjustments before generation.
- [ ] Vendor a pinned compatible Phaser 3 distribution from an official distribution source with license/provenance; verify the artifact and version.
- [ ] Give the manager spec §7's product brief. Manager refines real backlog; record PO scope/priority/acceptance decisions. Baseline excludes score and overlay; collision stops play and a documented key restarts.
- [ ] Configure artifact paths under `docs/ai/` using the verified format. Trace planned stories to acceptance criteria and approved plans.

### Task 7: Team delivery and baseline acceptance

**Files:** Worker-produced game files and handoffs, manager-maintained backlog/decisions, `docs/verification.md`.
**Interfaces:** Consumes approved backlog/configuration. Produces accepted baseline and delivery evidence.

- [ ] Manager starts research/planning as needed and presents the plan. Record approval and any rationale for skipped research.
- [ ] Implementation worker produces game, HTML entry point, static-server wrapper, and verification through the actual workflow. Manager does not write production code. Capture task/session/revision and handoff links.
- [ ] Browser-check load, arrow movement, hazards, collision stopping play, restart reset, and absence of score/overlay. Inspect network requests to confirm local asset loading. Tests alone do not replace play verification.
- [ ] Independent reviewer checks criteria, diff, and verification. Resolve important findings through the worker and re-review affected behavior.
- [ ] Present playable result for actual PO acceptance. Preserve accepted immutable revision; tag `golden-baseline` when committing/tagging is authorized. A dirty tree is not a reproducible accepted revision.
- [ ] From a fresh checkout of that revision, run the documented static server and repeat gameplay checks without agent installation. Keep baseline independently available.

### Task 8: Portfolio evidence and G2

**Files:** DEMO case study, decision log, portfolio summary, verification, media/index.
**Interfaces:** Consumes accepted baseline and real team artifacts. Produces complete portfolio demo without live update.

- [ ] Write `docs/DEMO.md`: product goal, ForgeStack engineering, team roles, meaningful PO decision, handoff, review, acceptance. Attribute upstream tools accurately.
- [ ] Write `docs/decision-log.md` explaining integration decisions, G1 evidence, scope, limitations; write `docs/portfolio.md` linking engineering, AI, and management evidence separately.
- [ ] Capture/edit real team workflow recording and gameplay clip. Disclose cuts/prior runs; remove secrets/unnecessary private content. Store locally or at an authorized durable location, indexed in `recordings/README.md`.
- [ ] Rehearse a 5–7 minute walkthrough: game → product goal/team → PO decision → handoff/review → accepted result. Verify presentation-machine playback.
- [ ] Declare G2 only with fresh-checkout gameplay, traceable evidence, actual acceptance, required recordings, and playback verification. Unavailable recording leaves that artifact incomplete; do not silently defer it.

## Phase 3 — Optional live update

### Task 9: Rehearse and demonstrate only if selected

**Files:** DEMO update story, updated game/phase artifacts, decisions, verification, recording.
**Interfaces:** Consumes accepted baseline and spec §8. Produces accepted updated revision and truthful fallback.

- [ ] Prepare isolated baseline checkout/worktree. Submit PO request for performance feedback to manager.
- [ ] Refine/approve score rule, overlay, Restart criteria; create real task. Use same team workflow with research only when warranted.
- [ ] Record actual planning, implementation transition, execution, independent review, PO acceptance. Verify increasing top-left score, frozen loss state/final-score overlay, Restart resetting all state.
- [ ] Preserve accepted update as separate revision; tag `golden-update` when authorized. Verify baseline and update both remain runnable; future rehearsals begin from baseline.
- [ ] Save and test playback of the real update recording. On live agent/network/runtime failure, stop live operation and show clearly labeled prior run. Synthetic transition messages are not a fallback.
- [ ] Rehearse selected ending: actual transition from approved planning, or complete accepted update. Confirm 5–7 minute timing and fallback. Record G3 independently; its absence does not invalidate G2.

## Self-review and execution handoff

Coverage: spec purpose/roles → Tasks 3–8; runtime contract → Task 1; hardening → Task 2; coordination → Tasks 3–4; G1 → Task 5; baseline → Tasks 6–7; artifacts/G2 → Task 8; optional update/G3 → Task 9.

Unknown upstream syntax is resolved in Task 1 before dependent implementation. This is a staged plan with a mandatory discovery checkpoint, not a claim that external integration details are already verified. Amend concrete implementation steps from that evidence before coding.

Review spec and plan together. Start Phase 1 when implementation is requested. Inline execution is available; delegation requires applicable agent/model/assignment approval. No code implementation, runtime sessions, or external project writes are part of this documentation revision.
