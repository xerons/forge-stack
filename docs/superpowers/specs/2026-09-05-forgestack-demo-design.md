# ForgeStack Demo — "Create a small game prototype" — Design

**Date:** 2026-09-05
**Status:** Approved (design sections 1-4 confirmed)
**Builds on:** ForgeStack v0.2 (phase model, managed-file manifest, asset install, setup --scope)

## 1. Purpose

Plan and build ForgeStack's **first demo**: demonstrate the tool creating a small
freshly-generated web game prototype, run live at a pitch with a committed golden path
as fallback. The demo doubles as a **portfolio centerpiece across four disciplines** —
Engineering, AI, Project Management, Game Development — and produces a shareable,
browser-runnable game prototype plus a reusable case study.

### Goals

- Show ForgeStack turning a plain repo into a game prototype through its
  `research → planning → running → review` phase model.
- Open with a finished, playable game *"created by ForgeStack"*, then go live with a
  second, fast-finishing **update story** through the same configured phases.
- Land a portfolio artifact bundle (repo + case study + captured runs + game + decision log).
- Never depend on live success: a playable game exists in the golden path at all times.

### Non-goals

- No new ForgeStack features (demo uses v0.2 surface as-is).
- No AGTX runtime repair beyond a bounded probe of what's reliable.
- No second game, no multiplayer/networking, no packaging/distribution of the game.

## 2. Demo surface (what ForgeStack actually shows)

| Command | Role in demo |
|---|---|
| `forgestack setup [--scope global\|project]` | Detects tools, installs ForgeStack skill suite + AGTX plugin, hash-tracked via `.forgestack-managed.json` (user edits preserved) |
| `forgestack phases scaffold / design / apply` | Scaffold = deterministic phase shape; design = agent fills per-phase purpose/prompt; apply = render + diff + y/N write `plugin.toml` |
| Phase model | `research / planning / running / review` (+ `preresearch`), `{task}`-anchored prompts, per-phase agent/skills, opt-in planning `team` → coverage matrix |
| `forgestack status / doctor / inbox / board / manager` | Adapter health, human-inbox, board attach, manager via herdr |

Game-relevant skills in the ForgeStack suite the pipeline can invoke: `router`,
`prototype-fast`, `phaser-core`, `phaser-arcade-physics`, `game-feel`,
`game-design-document`, `game-jam`.

## 3. Confirmed decisions

| Decision | Choice |
|---|---|
| Audience | Portfolio across Engineering / AI / PM / Game Dev + external pitch + talk/video/blog artifact |
| Game | Web (Phaser/JS), zero-install browser-runnable, freshly generated each run |
| Live vs staged | Hybrid — committed golden path as fallback; live guided run at pitch |
| Portfolio | Full artifact bundle: demo repo + `docs/DEMO.md` case study + captured terminal replay + gameplay clip + tech-decision log + portfolio summary page |
| Demo length | 5-7 min (short); natural off-ramp at the plan→next-phase card move |
| Default agent | **Codex** for `phases design` + running phase |
| AGTX runtime | Bounded probe first; outcome picks (A) native AGTX loop vs (B) AGTX-independent agent-command orchestration; golden path committed regardless |
| Update story | Second card through the SAME configured phases (research→planning, stop at transition). No re-run of `phases` mid-demo. |

## 4. Narrative arc (approved by user)

> "we build one game prototype, show the game while demo tell them this was created by
> forgestack, then proceed to use forgestack to create game update story as forgestack demo.
> after that i can either end demo there when card move from plan to next phase or can run
> to the end and show updated prototype."

1. **Pre-built golden path** — build one complete game prototype via ForgeStack (committed).
2. **Open the demo** — show the finished game; *"this was created by ForgeStack"*.
3. **Live run** — use ForgeStack to create a **game update story** (task 2) driven through
   the ForgeStack-configured phase pipeline.
4. **Flexible ending** — stop at the plan→next-phase card move (workflow + PM state)
   **or** run to the end and show the updated prototype.
5. Golden-path replay remains the committed fallback for the live portion.

Properties: pre-built game satisfies "freshly generated"; live segment is a short,
fast-finishing update (not a greenfield build); the PM angle (watching a card move
phases) is the natural off-ramp; determinism honored because the update is a fresh run
against a real repo.

## 5. Architecture & components (Section 1 — approved)

### Golden-path repo (the demo project)

A ForgeStack-enabled project with a committed, playable Phaser game:

```
<demo-repo>/
  .forgestack.toml            # phase config: research/planning/running/review, codex
  .agtx/plugins/forgestack/plugin.toml   # via `forgestack phases apply`
  .forgestack-managed.json    # manifest story (setup/apply writes are tracked)
  game-source/                # committed Phaser game
  run-game.html / run script  # static server → browser
  docs/DEMO.md                # case study (PM + engineering narration)
```

**Live demo surface** (at pitch): `forgestack phases` + card/status view + browser game.
Everything else (setup, apply, manifest) is shown in the golden path / replay.

### Deliverables

- Demo repo (shareable link)
- `docs/DEMO.md` case study
- Captured terminal replay (script/asciinema) + gameplay clip
- Tech-decision log (why Phaser, why hybrid live/golden-path, why this phase model)
- Portfolio summary page

## 6. Data flow (Section 2 — approved)

- **ForgeStack `phases` configure the MODEL** (phase shape: which phases, prompts, agents,
  skills, team) — **not individual tasks**. Tasks/cards are AGTX domain.
- One scaffolded phase model is baked into the golden-path repo.
- The update story is a **second card** flowing through the **same configured phases**
  (research → planning, stopping at the transition). The live demo shows the
  ForgeStack-configured phase model driving the update card.
- Live demo does **not** re-run `phases` mid-demo.
- No `--append` feature exists; the demo explicitly does not need it.

## 7. Error handling & contingencies (Section 3 — approved, defaults locked)

| Failure | Contingency |
|---|---|
| AGTX runtime not reliable | Live segment uses (B): ForgeStack `phases` + agent-CLI orchestration; AGTX hop stays out of the live path. Chosen via the bounded probe (implementation task, runs first in the plan). |
| Agent CLI fails/hangs/empty output | Abort the story; show the prepared golden-path update applied instead ("same story, pre-run"). One bounded timeout on agent calls (120s default in `phases design`). |
| No network / tools missing | `phases apply` from committed golden-path config — zero network. Everything except the agent call is local. |
| Screen/encoding hiccups | Replay the captured golden-path video for any segment; keep the pre-recorded run as a **local file**, not a stream. |
| "What happens next?" from audience | Decided before the demo: either continue running or cut. Do not improvise. |
| Rehearsal gate | Full dry run (captured) + a second as-audience pass on the final edited video, same demo conditions. Any issue surviving rehearsal triggers a fallback decision. |

## 8. Testing / rehearsal / verification (Section 4)

- **Golden-path build gate:** game must be committed and playable from a fresh clone
  with no setup beyond a static server, BEFORE demo prep. "A playable game exists at every moment."
- **Probe verdict (bounded implementation task):** single deliverable is a recorded
  verdict (A) or (B). Runs first in the plan; everything downstream branches off that one line.
- **Rehearsal:** (1) full dry run with the real agent, timeskips where the video will cut,
  every contingency exercised; capture clean replay + gameplay clip.
  (2) as-audience pass: final edited video, timed 5-7 min, on the demo machine / same
  projector-zoom conditions.
- **Verification checklist (demo repo):**
  - Fresh clone → `forgestack setup --scope project` → game runs; idempotent re-run
    (manifest preserves edits).
  - `forgestack phases apply` produces `plugin.toml`; `status`/`doctor` clean.
  - Update story's committed end-state (game change visible in browser) exists
    independently of live codex.
  - Every command in the transcript is pre-typed/aliased; no mid-demo typing.
- **Out of test scope:** AGTX daemon multitasking, multi-agent parallelism, other engines
  (kept to the probe).

## 9. Key risk review

- `agtx --help` headless → `Error: Device not configured (os error 6)`; under PTY it hangs.
  AGTX runtime is the only component that might not cooperate live — mitigated by the
  probe → (A)/(B) decision + committed golden path.
- ForgeStack `phases design` invokes the agent CLI directly (subprocess, `_AGENT_CMDS`),
  independent of AGTX — so `phases scaffold → design → apply` can be demonstrated with
  AGTX offline.

## 10. Implementation plan shape (for writing-plans)

1. **AGTX probe** (bounded) → recorded verdict (A)/(B).
2. **Golden-path build** → ForgeStack-enabled repo + committed Phaser game via the
   phase pipeline; verify fresh-clone bootstrap.
3. **Commit the update story's pre-run end-state** so it exists independently of live agents.
4. **Artifact production** → captured replay + gameplay clip + `docs/DEMO.md` + decision log + portfolio page.
5. **Rehearsal passes** (dry run + as-audience) → final video, timed.