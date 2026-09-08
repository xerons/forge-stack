# ForgeStack AI Team Portfolio Demo — Design

**Date:** 2026-09-05 (revision 3)
**Status:** Revised for the agreed two preparation phases and optional live update; readiness remains unverified.
**Replaces:** The earlier game-generation/phase-prompt demo design at this path.
**Plan:** [Implementation plan](../plans/2026-09-05-forgestack-demo.md)

## 1. Purpose

Demonstrate: **“I engineered ForgeStack to coordinate my own AI development team. I act as Product Owner, and the team produces a playable game prototype.”**

ForgeStack owns integration, configuration, workflow policy, skills, and user-facing entry points. AGTX owns task state and worker lifecycle; Codex supplies the executing agents. Attribute each tool accurately. The prototype is the team's delivered product and evidence of the workflow working.

| Portfolio skill | Required evidence |
| --- | --- |
| Engineering | ForgeStack integration changes, architecture decisions, regression checks, reproducible setup |
| AI | Persistent manager, distinct worker sessions, phase instructions, artifact handoffs, independent review |
| Project management | Product goal, prioritized backlog, scope decisions, blocker handling, progress reports, PO acceptance |

The team is Scrum-inspired. Do not claim formal ceremonies or roles that the run does not demonstrate. A prompt simulating several perspectives is not evidence of several executing agents.

## 2. Delivery phases and gates

### Phase 1 — Fix and verify ForgeStack

Make the smallest integration corrections required for the manager/team/PO loop. Prove it using a tiny non-game readiness story in an isolated Git project.

**G1:** A recorded real run demonstrates PO input → manager refinement → approved plan → worker implementation → independent review → PO acceptance, including one clarification and one failure/recovery exercise. Real task transitions and worker sessions must be inspectable through supported interfaces. Unit checks alone do not satisfy G1.

If AGTX lacks required supported operations, record the exact limitation and stop before Phase 2. Do not substitute fabricated transitions, direct database edits, or a one-prompt execution script. Replacing the workflow engine requires a new scope decision.

### Phase 2 — Use ForgeStack + Codex to produce the prototype

Use the verified integration in a separate demo Git repository. The PO gives a product brief; the manager refines and coordinates it; workers produce a playable game with saved delivery evidence.

**G2:** A fresh checkout runs the accepted game from a local static server. The repository contains traceable backlog, PO decisions, handoffs, verification, independent review, and acceptance. A recorded walkthrough and case study explain the engineering, AI, and management evidence.

**G2 is sufficient for a complete portfolio demo. No live update is required.**

### Phase 3 — Optional live update

Show the accepted prototype and ask the same team to deliver a small update. Stop after the approved plan transitions into actual implementation, or continue through review and PO acceptance and show the updated game.

**G3, only if selected:** Rehearse from the accepted baseline, save a verified updated revision and a recording of its real workflow, and rehearse fallback playback. A failed live run uses this recording, explicitly labeled as a prior run.

## 3. Roles and authority

| Role | Responsibility | Boundary |
| --- | --- | --- |
| Human PO | Product goal, priority, scope choices, final acceptance | Need not operate each worker or advance every phase |
| Persistent AI manager/facilitator | Refine intake, prepare tasks, coordinate workers, summarize progress, surface blockers, route PO answers, record decisions | Does not implement production code or keep a competing task database |
| Research/planning worker | Investigate; produce plan, acceptance criteria, dependencies | Does not invent unresolved product decisions |
| Implementation worker | Implement approved plan, test, produce handoff | One writer per shared working tree |
| Independent reviewer | Review spec, diff, tests, evidence; return findings | Separate session from implementation author; no feature implementation |
| ForgeStack + AGTX | Configure integration and operate real task/session lifecycle | AGTX remains authoritative for task state |

Codex is the default provider. Roles may use the same provider/model, but the manager remains separate from delivery workers and review uses an independent session. Parallel workers are unnecessary.

Spawning follows applicable user/AGENTS.md approval requirements. Product approval, worker-spawn permission, and final acceptance are separate events; none may be silently bypassed.

## 4. Current foundations and required corrections

Source inspection establishes these starting points, not installed-tool compatibility:

- Manager, intake, artifact-handoff, human-inbox, and workflow-policy skills already describe the desired coordination behavior.
- The phase model supports per-phase providers, skills, prompts, and artifact paths.
- The manager command currently launches bare Herdr without explicitly initializing the configured manager agent and instructions.
- Phase application writes the plugin but prints AGTX routing for manual installation. Effective routing and plugin activation need verification.
- Planning `team` is prompt-level role simulation with optional delegation, not guaranteed worker provisioning.
- Inbox queries only `needs_review` and can report a failed query as a clean inbox. It does not implement the complete answer-routing loop.
- Status reports installed tools/versions rather than task progress.
- Research-flag rendering and TOML escaping/parse validation need the hardening identified in the earlier design.

Phase 1 must correct manager initialization and truthful failure reporting, and verify task operations, routing, handoffs, and human decisions. Prefer supported upstream capabilities and existing skills. Documented manual configuration during setup is acceptable; manually orchestrating every delivery step is not the target experience.

Herdr may remain a workspace UI. A verified direct interactive Codex manager session is acceptable if it loads the same manager instructions and coordinates the same AGTX workers. Opening a workspace alone does not count as starting a manager.

## 5. Runtime and evidence contract

Record installed versions and exact supported interfaces for:

1. Create/read/update tasks and approved content.
2. Start phases and inspect actual state, worker identity, completion, and failure.
3. Activate the ForgeStack plugin and effective per-phase provider routing.
4. Hand approved artifacts to implementation and review.
5. Surface questions/blockers and deliver PO answers to the correct worker.
6. Start independent review and return important findings to implementation.
7. Record PO acceptance without equating worker exit code zero with acceptance.

Use installed help/source and bounded probes; do not guess CLI syntax. If a supported UI is required, record that boundary and prove the manager can operate the required workflow with available supported tools. Do not invent an unattended interface.

Persist concise artifacts in Git-backed project files. Evidence identifies task, role/session, artifact or revision, observed result, and PO decision. Keep credentials and unnecessary raw transcripts out of committed evidence.

Prompt wording alone does not enforce gates: G1 must show that implementation waits for approval, unresolved product questions are escalated, and acceptance comes from the PO.

## 6. Readiness story

Use an isolated disposable project:

> Create `greeting.py` exposing `greet(name: str) -> str`. It should return a friendly greeting. Clarify how a blank name should behave before implementing.

The manager asks the PO to choose blank-name behavior and records the actual answer. The worker implements `greet("Ada") == "Hello, Ada!"` and the selected blank-name behavior with tests. A separate reviewer checks the result; the PO accepts or rejects it.

Exercise one controlled blocked-worker or failed-query condition using an isolated fixture or supported runtime control. Do not invalidate real credentials. Show visible failure and recovery. If review finds important defects, demonstrate correction and re-review.

## 7. Prototype scope

**Project:** Separate sibling Git repository, proposed path `<sibling-demo-project>`. Check whether it exists and preserve its contents. Respect filesystem permissions at execution time.

**Brief:** A small Phaser 3 game: dodge falling objects with left/right arrow keys, rendered at 960×540 using simple original geometric visuals. Display controls. Collision stops play; a documented restart key begins a fresh run.

**Baseline acceptance:**

- Starts from `run-game.html` served by a local static server.
- Arrow keys move the player; falling hazards produce an observable loss condition.
- Collision stops play; restart resets game state.
- No score counter, final-score display, or Game Over overlay.
- Phaser is bundled locally with license/provenance; gameplay needs no network.
- No audio, persistence, leaderboard, multiplayer, or build tooling.

Manager and PO may refine the backlog within this scope. Production implementation must come from the worker workflow. Keep the prototype small without an artificial source-line limit. Verify selected game skills against the chosen Phaser version.

“Offline” applies to gameplay and local recordings. Live Codex execution may require network/authentication. Audience playback requires no agent installation; the operator needs the documented toolchain.

## 8. Optional update story

**Title:** Add score + game-over overlay.

**PO request:** “I want players to see how well they performed and restart easily after losing.”

Manager proposes a score increasing during survival, displayed top-left; collision freezes play and shows a “Game Over” overlay with final score and Restart button. PO confirms scoring rule and scope before implementation.

**Acceptance:** Score visibly increases; collision freezes play and shows final score; Restart resets score and state. No audio, persistence, or leaderboard.

Start each rehearsal from the accepted baseline, not the updated revision. Research may be skipped with a recorded rationale. Use the same configured workflow; do not reconfigure phases midway through delivery.

## 9. Portfolio artifacts and presentation

Required after Phase 2:

- ForgeStack readiness report: versions, actual commands/results, failures, fixes, G1 evidence.
- Demo repository and immutable accepted baseline revision with README/static-server instructions.
- `docs/product-brief.md`, `docs/backlog.md`, `docs/decisions.md`, phase artifacts under `docs/ai/`.
- `docs/verification.md`: observed gameplay checks, independent review, actual PO acceptance.
- `docs/DEMO.md`, `docs/decision-log.md`, `docs/portfolio.md`: evidence for all three skills and accurate upstream attribution.
- Local recording of the real team workflow and short gameplay clip, committed or linked through a durable artifact location, with tested playback instructions.

Phase 3 optionally adds an accepted updated revision and recording of that same update story. Baseline stays independently runnable.

Target 5–7 minutes: gameplay → product goal/team roles → meaningful PO decision → handoff/review → accepted result. Disclose edits and time cuts. Optional live delivery replaces part of this walkthrough; it is not a preparation prerequisite.

## 10. Verification and boundaries

- Regression tests cover configuration serialization, manager launch, upstream failures, and new integration behavior.
- Real G1 execution proves coordination; mocks do not substitute for it.
- Fresh-checkout gameplay and evidence review establish G2.
- Optional G3 includes timed rehearsal and recorded fallback playback.
- Record actual outcomes; never pre-fill successful checks or PO acceptance.
- No new workflow engine, supervisor, generalized scheduler, or game platform is in scope.
- This documentation revision does not authorize implementation, external publication, worker spawning, or committing user changes.
