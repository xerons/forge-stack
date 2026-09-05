# ForgeStack Demo — "Create a small game prototype" — Design

**Date:** 2026-09-05 (spec review rev. 2)
**Status:** Revised per spec review findings 1–6 (blocking findings 1–2 resolved)
**Builds on:** ForgeStack v0.2 (phase model, managed-file manifest, asset install, setup --scope)

### Revision summary (spec review, 6 findings)

| # | Finding | Resolution (this revision) |
|---|---|---|
| 1 | Live update orchestration undefined (no card create/advance command exists) | §7 defines the two concrete drivers: exact AGTX command set (path A, probe-gated) OR the committed orchestration script running phase prompts against the configured agent (path B). No unbacked "AGTX-independent orchestration" prose. |
| 2 | Fallback can't show PM workflow | §7 + §8: fallback for the card-move moment is the **pre-recorded phase replay clip** (local file) of that exact update story moving research→planning→running; golden path still ends with the updated game open in the browser. Narrative unchanged; fallback is explicitly a recorded replay. |
| 3 | Update story has no concrete requirement | §6.1 adds a fixed story: title, body, baseline, change, browser-visible acceptance criteria. Rehearsal/verification now measurable. |
| 4 | `research` boolean vs phase list conflict | §5.1 + implementation: phase **list is canonical**; renderer drops a `research` phase when `workflow_research=false`; validate warns on mismatch. Small in-scope hardening. |
| 5 | offline/zero-install underspecified; game skills not in ForgeStack suite | §2 + §5.2: game skills live in the user's skill dirs (documented precondition, not vendored); **Phaser is bundled locally** in the demo repo (no CDN) so the game runs offline from a static file. |
| 6 | Agent-authored prompts break TOML (`"""` unescaped) | §8: serializer escaping + `tomllib.loads()` validation gate before any write. Small in-scope hardening. |

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

- No new ForgeStack features (demo uses v0.2 surface as-is). Exception: the two small
  hardening fixes in §8.1 (research-flag respected; TOML escaping + parse gate) are
  explicitly in scope because the demo's golden-path `plugin.toml` cannot be reliable
  without them.
- No AGTX runtime repair beyond a bounded probe of what's reliable.
- No second game, no multiplayer/networking, no packaging/distribution of the game.

## 2. Demo surface (what ForgeStack actually shows)

| Command | Role in demo |
|---|---|
| `forgestack setup [--scope global\|project]` | Detects tools, installs ForgeStack skill suite + AGTX plugin, hash-tracked via `.forgestack-managed.json` (user edits preserved) |
| `forgestack phases scaffold / design / apply` | Scaffold = deterministic phase shape; design = agent fills per-phase purpose/prompt; apply = render + diff + y/N write `plugin.toml` |
| Phase model | `research / planning / running / review` (+ `preresearch`), `{task}`-anchored prompts, per-phase agent/skills, opt-in planning `team` → coverage matrix |
| `forgestack status / doctor / inbox / board / manager` | Adapter health, human-inbox, board attach, manager via herdr |

Game-relevant skills the pipeline can invoke: the ForgeStack suite ships `skills/forgestack/`
(workflow/PM suite: `phase-designer`, `intake`, `status`, `artifact-handoff`, `manager`,
`knowledge-sync`, `workflow-policy`, ...) — it does **not** ship game skills. The game-gen
prompts reference play-development skill packs (`router`, `prototype-fast`, `phaser-core`,
`phaser-arcade-physics`, `game-feel`, `game-design-document`, `game-jam`) that must already
exist in the executing agent's skill directories (`~/.claude/skills/`, `~/.agents/skills/`).
This is a **documented precondition**, not vendored content. If any pack is missing, the
running agent silently gets no skill — so the plan task for the golden-path build must
verify each referenced pack resolves before the game is committed.

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
  vendor/phaser.min.js        # Phaser BUNDLED LOCALLY — no CDN, game runs fully offline
  run-game.html / run script  # static server → browser
  docs/stories/update-score-over.md   # the fixed update story (§6.1)
  docs/DEMO.md                # case study (PM + engineering narration)
```

**Live demo surface** (at pitch): `forgestack phases` + card/status view + browser game.
Everything else (setup, apply, manifest) is shown in the golden path / replay.

**Offline / zero-install meaning (finding 5):** the *audience* installs nothing and the
game runs from a static file with no network — Phaser is vendored locally.
The *operator* needs the documented skill packs present and the configured agent CLI;
ForgeStack itself is already installed. If a demo machine has no agent CLI, the replay
fallback (§7) is used.

#### 5.1 Canonical phase representation (finding 4)

The **phase list (`[[workflow.phases]]`) is the single source of truth** for what renders.
`workflow_research` is a compat flag, not a second source of truth:

- Renderer: a phase with `key == "research"` renders only when `workflow_research` is true
  (this is a small in-scope hardening; today it renders unconditionally).
- Validation: a `research` phase present while `workflow_research=false` is a warning.
- The golden-path repo keeps `workflow_research=true` and a `research` phase, so the demo
  exercise the canonical (research-on) path.

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

### 6.1 The fixed update story (finding 3 — concrete, measurable)

The update story is one fixed task, committed in the golden-path repo as `docs/stories/update-score-over.md`,
so rehearsal, the replay fallback, and the live run all target the same change:

- **Card title:** "Add score + game-over overlay"
- **Card body (task):**
  > The current game has no score. Add: (1) a score counter that increases as the player
  > survives/dodges (any consistent rule the playable baseline makes obvious), displayed
  > top-left during play; (2) on player death, freeze the game and show a "Game Over" overlay
  > with the final score and a **Restart** button that reloads a fresh run. No audio, no
  > persistence, no leaderboard.
- **Baseline (committed, must be true before the story starts):** the golden-path game
  plays per its README; there is no score counter and no game-over overlay.
- **Observable acceptance criteria (browser-visible, order-independent):**
  1. During play a numeric score appears top-left and increases.
  2. On player death the game freezes and an overlay reads "Game Over" with the final score.
  3. Clicking **Restart** starts a fresh run (state reset).
- **Demo stopping gate:** the card has moved out of `planning` (research→planning shown
  live); from there the demo ends, or runs to the end and the three acceptance criteria
  are shown in the browser.
- **Determinism:** the story is the same every run; only the agent's prose/diff varies.
  A failing or divergent acceptance criterion is handled by the contingencies in §7.<br>
- **Skill packs referenced by the running phase (all verified present in user skill dirs, found at spec review):**
  `router`, `prototype-fast`, `phaser-core`, `phaser-arcade-physics`, `game-feel`,
  `game-design-document`, `game-jam`.

## 7. Error handling & contingencies (Section 3 — approved, defaults locked)

### 7.1 The two concrete live drivers (finding 1)

The live update story must move a card through phases. ForgeStack v0.2 has **no command
that creates/advances a card** — so the live driver is exactly one of these two,
selected by the bounded AGTX probe (implementation task, runs first):

- **Path A — native AGTX driver.** The probe must record the *exact* commands that create
  a task, move it research→planning→review, and list cards/status, e.g.
  `agtx task create "..." --status planning`, `agtx task move <id> --status running`,
  `agtx status`. Only commands **recorded working** in the probe may be used; any AGTX
  command that hangs/errors (today: `--help` → `Device not configured`, PTY hang) is
  excluded from the live path. If the probe records fewer than three reliable commands,
  the verdict is **B**, not an improvised hybrid.
- **Path B — committed orchestration script.** The demo repo ships
  `scripts/drive_story.py` which runs the **running-phase prompt** from the applied
  `plugin.toml` against the configured agent CLI (`codex exec`), waits for completion,
  then prints a card-move line (`planning → running → review`). This is the SAME
  mechanism `forgestack phases design` already uses (`_AGENT_CMDS` subprocess); the
  script is demo-domain glue in the demo repo, not a new ForgeStack feature. It reads
  the prompt from the committed `plugin.toml`, so it exercises the ForgeStack-configured
  phase model.

Both paths drive the **same** update story (§6.1). The one-line branches depend only on
the probe verdict.

| Failure | Contingency |
|---|---|
| AGTX runtime not reliable | Path B (committed `scripts/drive_story.py`) is the live driver; no AGTX in the live path. |
| Agent CLI fails/hangs/empty output | Abort the story; show the prepared golden-path update applied instead ("same story, pre-run"). One bounded timeout on agent calls (120s default) — the script enforces a hard timeout and returns a clean "timeout" message. |
| No network / tools missing | `phases apply` from committed golden-path config — zero network. The running agent has no network need for this story (Phaser vendored, no CDN). |
| Card-move view unavailable (AGTX down, Path A rejected) | **Recorded replay fallback (finding 2):** the card-move moment is shown via the pre-recorded phase-replay clip (local file) of the *exact* update story moving research→planning→running. The golden path still ends with the updated game open in the browser. This is an explicit, rehearsed fallback, not improvisation. |
| Screen/encoding hiccups | Replay the captured golden-path video for any segment; keep the pre-recorded run as a **local file**, not a stream. |
| "What happens next?" from audience | Decided before the demo: either continue running or cut. Do not improvise. |
| Rehearsal gate | Full dry run (captured) + a second as-audience pass on the final edited video, same demo conditions. Any issue surviving rehearsal triggers a fallback decision. |

### 7.2 Fallback semantics (finding 2, sealed)

The golden path is *not* the fallback for the PM workflow — the **recorded phase-replay
clip** is. The golden path guarantees "a playable game exists"; the replay guarantees "the
card-move (PM) story is still shown even with zero live orchestration." Both are committed
artifacts of the demo repo (see §8).

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

### 8.1 In-scope hardening (findings 4 & 6, small code changes in ForgeStack itself)

These are prerequisites for a reliable demo and correct v0.2 behavior, not new features:

- **Finding 4 — research flag respected.** `render_plugin_toml` skips a `research` phase
  when `workflow_research` is false; `validate` warns on the mismatch. Add/extend unit
  tests in `tests/unit/test_render.py` / `test_validate.py`.
- **Finding 6 — generated TOML must always parse.** Agent-authored prompts are
  interpolated into `"""..."""` TOML literals (renderer.py:24,26 and config.py render).
  Add serializer escaping for `"""` in prompt text, and a `tomllib.loads()` **parse gate**
  before `phases apply` writes `plugin.toml` (and before `render_toml` is written by
  `agents`/`scaffold`). A prompt containing `"""` must not produce invalid TOML; if the
  gate fails the write is refused with a clear message. Unit tests in `test_render.py`
  and `test_phases_cmd.py`.
- **Goal:** the golden-path `plugin.toml` is proven parseable by `tomllib.loads()` in the
  verification checklist.

## 9. Key risk review

- `agtx --help` headless → `Error: Device not configured (os error 6)`; under PTY it hangs.
  AGTX runtime is the only component that might not cooperate live — mitigated by the
  probe → (A)/(B) decision + committed golden path.
- ForgeStack `phases design` invokes the agent CLI directly (subprocess, `_AGENT_CMDS`),
  independent of AGTX — so `phases scaffold → design → apply` can be demonstrated with
  AGTX offline.

## 10. Implementation plan shape (for writing-plans)

1. **In-scope hardening (findings 4 & 6):** research-flag respected in renderer + validation
   warning; TOML escaping + parse gate before writes. Tests. (This unblocks everything
   downstream.)
2. **AGTX probe** (bounded) → recorded verdict (A) exact working AGTX commands, or (B)
   committed `scripts/drive_story.py` orchestration script (§7.1).
3. **Golden-path build** → ForgeStack-enabled repo + committed Phaser game (Phaser vendored
   locally) via the phase pipeline; verify fresh-clone bootstrap + `tomllib` parse + skill
   packs resolved.
4. **Commit the update story end-state + recorded phase-replay clip** of the same story
   (§6.1, §7.2) so the PM card-move is always showable.
5. **Artifact production** → captured replay + gameplay clip + `docs/DEMO.md` + decision log + portfolio page.
6. **Rehearsal passes** (dry run + as-audience) → final video, timed; every contingency in
   §7 exercised once.