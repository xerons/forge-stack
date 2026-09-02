# Customizable Phase Model Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let users define the workflow phase model (which phases, per-phase prompt/agent/skills/team) in ForgeStack config and re-render the AGTX `plugin.toml` + `[agents]` wiring from it, via a `forgestack phases` wizard (scaffold → agent design → apply).

**Architecture:** Config is the single source of truth. New `workflow` module owns the model (`PhaseDef`, default model), validation (AGTX grammar + registry), and rendering (plugin.toml + agents config). New `phases` CLI group scaffolds the shape deterministically, delegates content design to an agent, and applies with backup/diff/approval. AGTX remains the runtime authority — no lane names are invented.

**Tech Stack:** Python 3.11+, Typer, Rich, tomllib. Tests: pytest. Lint: ruff (line-length 100). Run: `.venv/bin/pytest tests/ -q`, `.venv/bin/ruff check src/`.

## Global Constraints

- Phase keys are limited to `{research, planning, running, review, preresearch}` (AGTX board grammar: `backlog → planning → running → review → done`; research optional; Done/Backlog structural). No new lane names.
- Per-phase agent routing is limited to the 4 named keys (`default_agent` + `[agents] research/planning/running/review`).
- `team` (multidisciplinary sprint-planning) is **opt-in and disabled by default**; only allowed on `planning`; ignored with a warning elsewhere. It costs extra tokens so never enable implicitly.
- At least one phase prompt must contain `{task}` or the phase is unreachable from Backlog.
- Model agents must resolve to `adapter.name` in the adapter registry; unresolvable → error list entry.
- Unknown skill names → warning entry (ok=True), not a failure.
- Project `[[workflow.phases]]` list replaces the global one wholesale (list override, not per-item merge).
- Default model when unset = current ForgeStack plugin behavior (research + planning + running + review, default prompts incl. the ponytail discipline paragraph in `running`).
- No third-party skill content vendored; `skills`/`team` are referenced strings only.
- A phase reachable from Backlog only when its prompt/command contains `{task}`.

---

### Task 1: Phase model + default model

**Files:**
- Create: `src/forgestack/workflow/__init__.py`
- Create: `src/forgestack/workflow/model.py`
- Test: `tests/unit/test_phases.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `PhaseDef(key, label, purpose, agent, skills, team, artifact, prompt)`, `PhaseModel(research: bool, cyclic: bool, phases: list[PhaseDef])`, constants `ALLOWED_PHASE_KEYS`, `AGENT_PHASE_KEYS`, `PhaseModel.default() -> PhaseModel`, `DEFAULT_PROMPTS: dict[str, str]` (keyed by phase key).

- [ ] **Step 1: Write the failing test**

`tests/unit/test_phases.py`:

```python
from forgestack.workflow.model import (
    ALLOWED_PHASE_KEYS,
    AGENT_PHASE_KEYS,
    PhaseModel,
)


def test_default_model_has_four_phases():
    m = PhaseModel.default()
    assert [p.key for p in m.phases] == ["research", "planning", "running", "review"]
    assert m.research is True
    assert m.cyclic is False


def test_default_model_prompts_have_task_placeholder():
    m = PhaseModel.default()
    assert all("{task}" in p.prompt for p in m.phases)


def test_phase_grammar_constants():
    assert ALLOWED_PHASE_KEYS == {"research", "planning", "running", "review", "preresearch"}
    assert AGENT_PHASE_KEYS == ("research", "planning", "running", "review")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/unit/test_phases.py -v`
Expected: FAIL with `ModuleNotFoundError: forgestack.workflow`

- [ ] **Step 3: Create the workflow module**

`src/forgestack/workflow/__init__.py`:

```python
"""Workflow phase model, validation, and AGTX rendering."""
```

`src/forgestack/workflow/model.py`:

```python
"""Phase model. Config is the source of truth; AGTX stays the runtime authority."""

from __future__ import annotations

from dataclasses import dataclass, field

ALLOWED_PHASE_KEYS = {"research", "planning", "running", "review", "preresearch"}
AGENT_PHASE_KEYS = ("research", "planning", "running", "review")


@dataclass
class PhaseDef:
    key: str
    label: str = ""
    purpose: str = ""
    agent: str = ""
    skills: list[str] = field(default_factory=list)
    team: list[str] = field(default_factory=list)
    artifact: str | None = None
    prompt: str = ""


@dataclass
class PhaseModel:
    research: bool = True
    cyclic: bool = False
    phases: list[PhaseDef] = field(default_factory=list)

    @classmethod
    def default(cls) -> PhaseModel:
        return cls(
            research=True,
            cyclic=False,
            phases=[
                PhaseDef(key="research", label="Research", prompt=DEFAULT_PROMPTS["research"]),
                PhaseDef(key="planning", label="Planning", prompt=DEFAULT_PROMPTS["planning"]),
                PhaseDef(key="running", label="Running", prompt=DEFAULT_PROMPTS["running"]),
                PhaseDef(key="review", label="Review", prompt=DEFAULT_PROMPTS["review"]),
            ],
        )


DEFAULT_PROMPTS: dict[str, str] = {
    "research": """Task:
{task}

You are in the RESEARCH / DISCOVERY phase.
Understand the problem before planning a solution.

Do:
1. Read the grooming brief, ticket, or kickoff notes.
2. Inspect relevant documentation and existing code.
3. Identify unclear requirements, assumptions, dependencies, and risks.
4. Investigate existing architecture and conventions.
5. Identify questions that genuinely require human/product input.
6. Resolve technical questions from the repository where possible.
7. Produce a concise research/discovery summary for Planning.

Do NOT implement production code, prematurely design the full solution, or invent product requirements.""",
    "planning": """Task:
{task}

You are in the PLANNING phase.
Turn the requirement into an implementation-ready contract.

Do:
1. Validate the intended user/business outcome.
2. Resolve remaining ambiguity.
3. Determine the architecture and technical approach.
4. Define domain rules, interfaces, constraints, and edge cases.
5. Define acceptance criteria and expected tests.
6. Produce an implementation-ready specification.
7. Produce a concrete implementation plan / work decomposition.
8. Reuse existing project conventions and architecture.

Do NOT implement production code.""",
    "running": """Task:
{task}

You are in the IMPLEMENTATION phase. The planning/specification phase is authoritative.

Implement the approved specification and plan.

Do:
1. Read the approved spec and plan completely.
2. Implement incrementally.
3. Follow existing architecture and project conventions.
4. Add or update tests.
5. Run relevant verification.
6. Perform a self-review before declaring completion.
7. Keep changes scoped to the approved task.

If ponytail discipline is available, apply its YAGNI/reuse/stdlib ladder and minimal-diff
guidance to avoid over-engineering. Otherwise follow the equivalent principles:
smallest change that works, no speculative abstraction, no scaffolding for later.

Do NOT silently modify or reinterpret approved requirements.""",
    "review": """Task:
{task}

You are in the independent REVIEW / QA phase. You did not author the implementation.
Treat the approved specification and acceptance criteria as authoritative.

Review separately for:
1. Specification and acceptance-criteria compliance
2. Correctness
3. Engineering/code quality
4. Test quality and missing regression coverage
5. Edge cases
6. Security concerns
7. Architectural consistency
8. Unnecessary scope or requirement drift

Classify findings as BLOCKING / IMPORTANT / OPTIONAL.
Do NOT implement new functionality during review.""",
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/unit/test_phases.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add src/forgestack/workflow tests/unit/test_phases.py
git commit -m "feat(workflow): add phase model and default prompts"
```

---

### Task 2: Config parsing + serialization of phases

**Files:**
- Modify: `src/forgestack/config.py` (Config dataclass ~:19-26, `from_dict`, `render_toml`, `_fmt_kv`)
- Test: `tests/unit/test_phases.py`

**Interfaces:**
- Consumes: `PhaseDef`, `PhaseModel` from `forgestack.workflow.model` (Task 1).
- Produces: `Config` gains `workflow_research: bool = True`, `workflow_cyclic: bool = False`, `phases: list[PhaseDef] = field(default_factory=list)`. `render_toml(config)` emits `[workflow] research`/`cyclic` and `[[workflow.phases]]` blocks. `_fmt_kv` also handles `list[str]` (emitted as `["a", "b"]`).

- [ ] **Step 1: Write the failing tests** (append to `tests/unit/test_phases.py`)

```python
from forgestack.config import Config, load_config, render_toml


def test_from_dict_parses_phases():
    data = {
        "workflow": {
            "engine": "agtx",
            "research": False,
            "cyclic": True,
            "phases": [
                {"key": "planning", "agent": "codex", "skills": ["matt"], "team": []},
                {"key": "running", "agent": "opencode"},
            ],
        }
    }
    cfg = Config.from_dict(data)
    assert cfg.workflow_research is False
    assert cfg.workflow_cyclic is True
    assert [p.key for p in cfg.phases] == ["planning", "running"]
    assert cfg.phases[0].skills == ["matt"]


def test_from_dict_empty_workflow_defaults():
    cfg = Config.from_dict({"profile": "x"})
    assert cfg.workflow_research is True
    assert cfg.workflow_cyclic is False
    assert cfg.phases == []


def test_render_toml_roundtrip_with_phases():
    data = {
        "workflow": {
            "research": False,
            "cyclic": True,
            "phases": [
                {"key": "planning", "label": "Planning", "agent": "codex", "artifact": "plan.md"}
            ],
        }
    }
    cfg = Config.from_dict(data)
    rendered = render_toml(cfg)
    import tomllib

    reparsed = Config.from_dict(tomllib.loads(rendered))
    assert reparsed.workflow_research is False
    assert reparsed.workflow_cyclic is True
    assert reparsed.phases[0].key == "planning"
    assert reparsed.phases[0].artifact == "plan.md"


def test_project_phases_replace_global():
    global_raw = {
        "workflow": {
            "phases": [
                {"key": "planning", "agent": "codex"},
                {"key": "running", "agent": "codex"},
                {"key": "review", "agent": "codex"},
            ]
        }
    }
    project_raw = {"workflow": {"phases": [{"key": "planning", "agent": "opencode"}]}}
    from forgestack.config import _deep_merge

    merged = _deep_merge(global_raw, project_raw)
    assert len(merged["workflow"]["phases"]) == 1  # wholesale replace, not item merge
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/unit/test_phases.py -v`
Expected: FAIL (from the Task 1 file, `PhaseDef` import now resolves — these Task 2 tests fail on `type object 'Config' has no attribute 'workflow_research'` etc., which is correct: the fields don't exist yet).

- [ ] **Step 3: Extend `Config` and parsers in `src/forgestack/config.py`**

Add fields to the `Config` dataclass (after `values: dict = field(default_factory=dict)`):

```python
    workflow_research: bool = True
    workflow_cyclic: bool = False
    phases: list[PhaseDef] = field(default_factory=list)
```

Extend the existing `@classmethod from_dict` (config.py lines 28-40) with the two workflow booleans and phase parsing — keep `wf.get("engine", "agtx")` and the existing field reads intact:

```python
    @classmethod
    def from_dict(cls, data: dict) -> Config:
        mgr = data.get("manager") or {}
        wf = data.get("workflow") or {}
        return cls(
            profile=str(data.get("profile", "default")),
            manager_agent=mgr.get("agent") if isinstance(mgr, dict) else None,
            workflow_engine=str(wf.get("engine", "agtx")) if isinstance(wf, dict) else "agtx",
            agents=dict(data.get("agents") or {}),
            integrations=dict(data.get("integrations") or {}),
            runtime_workspace=(data.get("runtime") or {}).get("workspace") if isinstance(data.get("runtime"), dict) else None,
            workflow_research=bool(wf.get("research", True)) if isinstance(wf, dict) else True,
            workflow_cyclic=bool(wf.get("cyclic", False)) if isinstance(wf, dict) else False,
            phases=_parse_phases(wf.get("phases")) if isinstance(wf, dict) else [],
            values=data,
        )
```

Keep existing `_deep_merge` and `load_config` as-is (list override already falls out of the recursive merge: non-dict values are replaced wholesale).

Add phase parsing helpers below `_fmt_kv`:

```python
def _parse_phases(raw: object) -> list[PhaseDef]:
    if not isinstance(raw, list):
        return []
    out: list[PhaseDef] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        key = str(item.get("key") or "")
        if not key:
            continue
        out.append(
            PhaseDef(
                key=key,
                label=str(item.get("label") or ""),
                purpose=str(item.get("purpose") or ""),
                agent=str(item.get("agent") or ""),
                skills=[str(s) for s in item.get("skills", [])],
                team=[str(t) for t in item.get("team", [])],
                artifact=str(item["artifact"]) if item.get("artifact") else None,
                prompt=str(item.get("prompt") or ""),
            )
        )
    return out
```

Extend `render_toml` so the `[workflow]` block (line 74) emits `engine` then `research`/`cyclic` then each phase as an array-of-tables block. `purpose`/`prompt` are emitted with TOML triple-quoted literal strings (`"""`) because prompts are multiline; plain single-line values go through `_fmt_kv` (which returns the full `key = value` line):

```python
    lines += ["[workflow]", _fmt_kv("engine", config.workflow_engine)]
    lines += [
        f"research = {str(config.workflow_research).lower()}",
        f"cyclic = {str(config.workflow_cyclic).lower()}",
        "",
    ]
    for p in config.phases:
        lines.append("[[workflow.phases]]")
        lines.append(_fmt_kv("key", p.key))
        if p.label:
            lines.append(_fmt_kv("label", p.label))
        if p.purpose:
            lines.append(f'purpose = """{p.purpose}"""')
        if p.agent:
            lines.append(_fmt_kv("agent", p.agent))
        if p.skills:
            lines.append(_fmt_kv("skills", p.skills))
        if p.team:
            lines.append(_fmt_kv("team", p.team))
        if p.artifact:
            lines.append(_fmt_kv("artifact", p.artifact))
        if p.prompt:
            lines.append(f'prompt = """{p.prompt}"""')
        lines.append("")
```

Extend `_fmt_kv` to emit non-empty lists as TOML arrays — **keeping the existing full-line `key = value` contract** used by the `[agents]`/`[integrations]` loops above it:

```python
def _fmt_kv(key: str, val) -> str:
    if isinstance(val, bool):
        return f"{key} = {'true' if val else 'false'}"
    if isinstance(val, list):
        items = ", ".join(f'"{v}"' for v in val)
        return f"{key} = [{items}]"
    return f'{key} = "{val}"'
```

Note: triple-quoted literal strings cannot contain `"""`; the default prompts do not. `_parse_phases` is defined after `_fmt_kv` but is fine being referenced by `from_dict` earlier in the file (resolved at call time).

Add the import at the top of `config.py`:

```python
from .workflow.model import PhaseDef
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/ -q`
Expected: PASS (all, including the previous 14)

- [ ] **Step 5: Lint + commit**

Run: `.venv/bin/ruff check src/ && .venv/bin/ruff check tests/`
Then:

```bash
git add src/forgestack/config.py tests/unit/test_phases.py
git commit -m "feat(config): parse and render workflow phases"
```

---

### Task 3: Phase model validation

**Files:**
- Create: `src/forgestack/workflow/validate.py`
- Test: `tests/unit/test_validate.py`

**Interfaces:**
- Consumes: `ALLOWED_PHASE_KEYS`, `AGENT_PHASE_KEYS`, `PhaseModel` (Task 1); `CheckResult` from `forgestack.adapters.protocol`.
- Produces: `validate(model: PhaseModel, registry: Iterable) -> list[CheckResult]` (name-colliding with the existing `Adapter.validate` is fine — different module).

- [ ] **Step 1: Write the failing tests**

`tests/unit/test_validate.py`:

```python
from forgestack.adapters.protocol import CheckResult
from forgestack.workflow.model import PhaseDef, PhaseModel
from forgestack.workflow.validate import validate


def _model(*phases, research=True, cyclic=False):
    return PhaseModel(research=research, cyclic=cyclic, phases=list(phases))


def _ok(name):
    return lambda r: r.name == name and r.ok


def test_valid_default_passes():
    m = PhaseModel.default()
    results = validate(m, [object() for _ in range(12)])  # registry opaque to validate's usage
    assert not [r for r in results if not r.ok]


def test_missing_planning_is_error():
    phases = [PhaseDef(key="research"), PhaseDef(key="running"), PhaseDef(key="review")]
    results = validate(_model(*phases), [])
    assert any(r.name == "planning" and not r.ok for r in results)


def test_bad_key_is_error():
    results = validate(_model(PhaseDef(key="populate", prompt="Task:\n{task}")), [])
    assert any(r.name == "phase populate" and not r.ok for r in results)


def test_no_task_placeholder_is_error():
    phases = [
        PhaseDef(key="planning", prompt="no placeholder"),
        PhaseDef(key="running", prompt="x"),
        PhaseDef(key="review", prompt="y"),
    ]
    results = validate(_model(*phases), [])
    assert any(r.name == "reachable" and not r.ok for r in results)


def test_unresolvable_agent_is_error():
    m = _model(PhaseDef(key="planning", agent="not-an-adapter"),
               PhaseDef(key="running"), PhaseDef(key="review"))
    results = validate(m, [])
    assert any(r.name == "agent:planning" and not r.ok for r in results)


def test_team_off_planning_is_warning_not_error():
    m = _model(PhaseDef(key="running", team=["artist"]), PhaseDef(key="planning"), PhaseDef(key="review"))
    results = validate(m, [])
    assert any(r.name == "team:running" and r.ok for r in results)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/unit/test_validate.py -v`
Expected: FAIL (`ModuleNotFoundError`)

- [ ] **Step 3: Implement `validate`**

`src/forgestack/workflow/validate.py`:

```python
"""Phase model validation against the AGTX grammar and adapter registry."""

from __future__ import annotations

from collections.abc import Iterable

from ..adapters.protocol import CheckResult
from .model import AGENT_PHASE_KEYS, ALLOWED_PHASE_KEYS, PhaseModel


def validate(model: PhaseModel, registry: Iterable) -> list[CheckResult]:
    results: list[CheckResult] = []
    keys = [p.key for p in model.phases]

    for p in model.phases:
        if p.key not in ALLOWED_PHASE_KEYS:
            results.append(
                CheckResult(
                    f"phase {p.key}",
                    False,
                    f"not in allowed keys {sorted(ALLOWED_PHASE_KEYS)}",
                )
            )

    dupes = sorted({k for k in keys if keys.count(k) > 1})
    if dupes:
        results.append(CheckResult("unique keys", False, ", ".join(dupes)))

    for required in ("planning", "running", "review"):
        if required not in keys:
            results.append(CheckResult(required, False, "required phase missing"))

    if not any("{task}" in (p.prompt or "") for p in model.phases):
        results.append(CheckResult("reachable", False, "no prompt contains {{task}}"))

    known = {getattr(a, "name", "") for a in registry}
    for p in model.phases:
        if p.agent and p.agent not in known:
            results.append(CheckResult(f"agent:{p.key}", False, f"{p.agent} not in registry"))

    for p in model.phases:
        if p.team and p.key != "planning":
            results.append(CheckResult(f"team:{p.key}", True, "team ignored outside planning"))

    return results
```

- [ ] **Step 4: Run tests to verify they pass + fix the agent-check subtlety**

Run: `.venv/bin/pytest tests/unit/test_validate.py -v`
Note: `test_valid_default_passes` passes a 12-item registry of `object()`s whose names are `""` — but default phases have empty `agent`, so the agtx check is vacuous. `test_unresolvable_agent_is_error` passes registry `[]`, so `known == set()`. Both work as written.

- [ ] **Step 5: Commit**

```bash
git add src/forgestack/workflow/validate.py tests/unit/test_validate.py
git commit -m "feat(workflow): validate phase model against agtx grammar"
```

---

### Task 4: AGTX plugin + agents renderer

**Files:**
- Create: `src/forgestack/workflow/renderer.py`
- Test: `tests/unit/test_render.py`

**Interfaces:**
- Consumes: `PhaseModel`, `DEFAULT_PROMPTS`, `AGENT_PHASE_KEYS` (Task 1).
- Produces: `render_plugin_toml(model: PhaseModel, plugin_name: str = "forgestack", plugin_description: str = "") -> str`; `render_agents_config(model: PhaseModel) -> dict[str, str]`.

- [ ] **Step 1: Write the failing tests**

`tests/unit/test_render.py`:

```python
from forgestack.workflow.model import PhaseDef, PhaseModel
from forgestack.workflow.renderer import render_agents_config, render_plugin_toml


def test_render_default_plugin_toml_matches_current_contract():
    out = render_plugin_toml(PhaseModel.default())
    assert 'name = "forgestack"' in out
    assert "cyclic = false" in out
    assert "[prompts]" in out
    for key in ("research", "planning", "running", "review"):
        assert f"{key} = \"\"\"" in out
        assert "{task}" in out


def test_render_cyclic_flag():
    m = PhaseModel.default()
    m.cyclic = True
    assert "cyclic = true" in render_plugin_toml(m)


def test_render_preresearch_as_command():
    m = PhaseModel.default()
    m.phases.append(PhaseDef(key="preresearch", purpose="Repo intro.", prompt="echo setup"))
    out = render_plugin_toml(m)
    assert "[commands]" in out
    assert "preresearch" in out


def test_render_artifacts():
    m = PhaseModel.default()
    m.phases[1].artifact = "plan.md"
    out = render_plugin_toml(m)
    assert '[artifacts]' in out
    assert "planning = \"docs/forgestack/plan.md\"" in out


def test_render_team_planning_prompt_contains_roles_and_matrix():
    m = PhaseModel.default()
    m.phases[1].team = ["Senior Unity3D dev", "Senior Artist", "UI expert"]
    out = render_plugin_toml(m)
    assert "Senior Unity3D dev" in out
    assert "coverage matrix" in out


def test_render_skills_paragraph():
    m = PhaseModel.default()
    m.phases[2].skills = ["ponytail"]
    out = render_plugin_toml(m)
    assert "ponytail" in out


def test_render_agents_config_only_four_keys():
    m = PhaseModel.default()
    m.phases[1].agent = "codex"
    m.phases[2].agent = "opencode"
    out = render_agents_config(m)
    assert out == {"planning": "codex", "running": "opencode"}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/unit/test_render.py -v`
Expected: FAIL (`ModuleNotFoundError`)

- [ ] **Step 3: Implement the renderer**

`src/forgestack/workflow/renderer.py`:

```python
"""Render a PhaseModel into AGTX plugin.toml and [agents] config."""

from __future__ import annotations

from .model import AGENT_PHASE_KEYS, DEFAULT_PROMPTS, PhaseModel


def render_plugin_toml(
    model: PhaseModel,
    plugin_name: str = "forgestack",
    plugin_description: str = "Research → planning → implementation → independent review",
) -> str:
    lines = [
        f'name = "{plugin_name}"',
        f'description = "{plugin_description}"',
        f"cyclic = {str(model.cyclic).lower()}",
    ]
    prompt_blocks: list[str] = []
    command_blocks: list[str] = []
    artifact_lines: list[str] = []
    for p in model.phases:
        if p.key == "preresearch":
            command_blocks.append(f'[commands]')
            command_blocks.append(f'preresearch = """{_phase_text(p)}"""')
            continue
        prompt_blocks.append(f'{p.key} = """{_phase_text(p)}"""')
        if p.artifact:
            artifact_lines.append(f'{p.key} = "docs/{plugin_name}/{p.artifact}"')
    if prompt_blocks:
        lines.append("")
        lines.append("[prompts]")
        lines += prompt_blocks
    if command_blocks:
        lines.append("")
        lines += command_blocks
    if artifact_lines:
        lines.append("")
        lines.append("[artifacts]")
        lines += artifact_lines
    return "\n".join(lines) + "\n"


def render_agents_config(model: PhaseModel) -> dict[str, str]:
    return {p.key: p.agent for p in model.phases if p.key in AGENT_PHASE_KEYS and p.agent}


def _phase_text(p) -> str:
    body = p.prompt.strip() if p.prompt else DEFAULT_PROMPTS.get(p.key, "Task:\n{task}")
    parts = [body]
    if p.skills:
        packs = ", ".join(p.skills)
        parts.append(
            "Available skill packs for this phase (use opportunistically, never vendor): "
            + packs + "."
        )
    if p.team and p.key == "planning":
        roles = ", ".join(p.team)
        parts.append(
            "Multidisciplinary sprint-planning (enabled): simulate this team working the "
            f"story together — {roles}. Run one explicit role pass per member (deliverables, "
            "owned requirements, risks, commonly-overlooked items); when this agent supports "
            "sub-agents, delegate each role pass to an internal specialist sub-agent, "
            "otherwise do a structured reasoning pass. Produce a requirements × roles "
            "coverage matrix in the planning artifact and flag any requirement uncovered "
            "by the team as a gap before decomposition. Still do not implement production code."
        )
    return "\n".join(parts)
```

Named capturing note: triple-quoted TOML requires `"""` ; the test asserts `f"{key} = \"\"\""`, which holds since the string literal `'"""'` is that exact character sequence. Validated at runtime by `tomllib.loads` in Task 6 tests.

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/unit/test_render.py -v`
Expected: PASS (7 passed)

- [ ] **Step 5: Verify rendered TOML parses**

Run: `.venv/bin/python -c "from forgestack.workflow.model import PhaseModel; from forgestack.workflow.renderer import render_plugin_toml; import tomllib; print(tomllib.loads(render_plugin_toml(PhaseModel.default()))['name'])"`
Expected: prints `forgestack`

- [ ] **Step 6: Commit**

```bash
git add src/forgestack/workflow/renderer.py tests/unit/test_render.py
git commit -m "feat(workflow): render agtx plugin and agents config"
```

---

### Task 5: `forgestack phases scaffold` (deterministic shape interview)

**Files:**
- Create: `src/forgestack/commands/phases_cmd.py`
- Modify: `src/forgestack/cli.py` (register the `phases` typer group)
- Modify: `src/forgestack/commands/setup_cmd.py` (delegate a "design workflow phases?" prompt to scaffold)
- Test: `tests/unit/test_phases_cmd.py`

**Interfaces:**
- Consumes: `Config`, `load_config`, `render_toml` from `forgestack.config`; `git_root` from `forgestack.paths`; `registry()` from `forgestack.adapters.registry`; `PhaseDef`, `PhaseModel` (Task 1); `_deep_merge` (Task 2).
- Produces: module-level `phases_app = typer.Typer(name="phases", help="Design and apply the workflow phase model.")` with subcommands `scaffold`, `design`, `apply`; `_agent_command(agent: str) -> list[str] | None`; scaffold writes the phase list into the active config scope (global or project via `--scope`).

- [ ] **Step 1: Write the failing tests**

`tests/unit/test_phases_cmd.py`:

```python
from typer.testing import CliRunner

from forgestack.commands.phases_cmd import _agent_command
from forgestack.cli import app

runner = CliRunner()


def test_phases_group_registered():
    result = runner.invoke(app, ["phases", "--help"])
    assert result.exit_code == 0
    assert "scaffold" in result.output
    assert "design" in result.output
    assert "apply" in result.output


def test_agent_command_map():
    assert _agent_command("codex") == ["codex", "exec"]
    assert _agent_command("unknown-agent") is None


def test_scaffold_writes_project_config(tmp_path, monkeypatch):
    import tomllib

    from forgestack.commands.phases_cmd import _write_scope

    proj = tmp_path / "proj"
    proj.mkdir()
    cfg_path = proj / ".forgestack.toml"

    _write_scope(
        cfg_path,
        phases=[
            {"key": "planning", "agent": "codex"},
            {"key": "running", "agent": "opencode"},
            {"key": "review", "agent": "codex"},
        ],
        research=False,
        cyclic=False,
    )
    raw = tomllib.loads(cfg_path.read_text())
    assert [p["key"] for p in raw["workflow"]["phases"]] == ["planning", "running", "review"]
    assert raw["workflow"]["research"] is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/unit/test_phases_cmd.py -v`
Expected: FAIL (`ModuleNotFoundError: forgestack.commands.phases_cmd`)

- [ ] **Step 3: Implement `phases_cmd.py`**

```python
"""forgestack phases — design and apply the workflow phase model."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.prompt import Confirm, Prompt

from ..adapters.registry import registry
from ..config import Config, _deep_merge, render_toml
from ..paths import git_root
from ..workflow import validate
from ..workflow.model import AGENT_PHASE_KEYS, ALLOWED_PHASE_KEYS, PhaseDef, PhaseModel

phases_app = typer.Typer(name="phases", help="Design and apply the workflow phase model.")

_DEFAULT_SELECTION = "planning,running,review"

_AGENT_CMDS = {
    "codex": ["codex", "exec"],
    "claude": ["claude", "-p"],
    "opencode": ["opencode", "run"],
}


def _write_scope(
    path: Path,
    phases: list[dict],
    research: bool,
    cyclic: bool,
) -> None:
    existing: dict = {}
    if path.exists():
        import tomllib

        existing = tomllib.loads(path.read_text())
    data = {"workflow": {"engine": "agtx", "research": research, "cyclic": cyclic, "phases": phases}}
    merged = _deep_merge(existing, data)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_toml(Config.from_dict(merged)))


@phases_app.command("scaffold")
def scaffold(scope: str = typer.Option("project", "--scope", help="project or global")) -> None:
    """Collect the deterministic shape: which phases, research/cyclic, agents, skills, team."""
    console = Console()
    root = git_root(Path.cwd()) if scope == "project" else None
    if scope == "project" and root is None:
        console.print("[red]Not a Git repository. Use --scope global.[/red]")
        raise SystemExit(1)

    providers = [a.name for a in registry() if getattr(a, "category", "") == "agents"]
    fallback = (providers or ["codex"])[0]

    choice = Prompt.ask(
        "Phases (comma-separated from research, planning, running, review, preresearch)",
        default=_DEFAULT_SELECTION,
    ).strip().lower()
    keys = [k for k in [s.strip() for s in choice.split(",")] if k]
    for k in keys:
        if k not in ALLOWED_PHASE_KEYS:
            console.print(f"[yellow]Ignoring unknown phase '{k}'[/yellow]")

    research = Confirm.ask("Enable optional research lane?", default=("research" in keys))
    cyclic = Confirm.ask("Cyclic flow (review back to planning)?", default=False)

    phases: list[dict] = []
    for k in keys:
        if k not in AGENT_PHASE_KEYS:
            phases.append({"key": k, "purpose": ""})
            continue
        agent = Prompt.ask(f"Agent for '{k}'", choices=providers or ["codex"], default=fallback)
        skills = Prompt.ask(f"Skill packs for '{k}' (comma-separated, optional)", default="")
        skills = [s.strip() for s in skills.split(",") if s.strip()]
        phase: dict = {"key": k, "agent": agent}
        if skills:
            phase["skills"] = skills
        if k == "planning" and Confirm.ask(
            "Add multidisciplinary team to planning? (extra tokens, opt-in)", default=False
        ):
            team = Prompt.ask("Team roster (comma-separated roles)", default="")
            phase["team"] = [t.strip() for t in team.split(",") if t.strip()]
        phases.append(phase)

    if scope == "project":
        from ..paths import project_config_path

        path = project_config_path(root)
    else:
        from ..paths import global_config_path

        path = global_config_path()
    _write_scope(path, phases, research, cyclic)
    console.print(f"Scaffold written. Next: [bold]forgestack phases design[/bold] to fill content.")


@phases_app.command("design")
def design(scope: str = typer.Option("project", "--scope", help="project or global")) -> None:
    """Co-design per-phase content with the configured agent."""
    console = Console()
    from ..config import load_config

    root = git_root(Path.cwd()) if scope == "project" else None
    cfg = load_config(root)
    if not cfg.phases:
        console.print("[yellow]No phases in config yet — run 'phases scaffold' first.[/yellow]")
        return
    model = PhaseModel(research=cfg.workflow_research, cyclic=cfg.workflow_cyclic)
    model.phases = cfg.phases

    agent = next((p.agent for p in cfg.phases if p.agent), None) or cfg.manager_agent or "codex"
    cmd = _agent_command(agent)
    if cmd is None or not git_root(Path.cwd()):
        console.print(
            f"[yellow]Agent '{agent}' has no one-shot launcher here. Edit purpose/prompt "
            "directly in your config, or run 'phases apply' to ship default prompts.[/yellow]"
        )
        return

    prompt = _design_prompt(model)
    try:
        import subprocess

        result = subprocess.run(
            cmd + [prompt],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except (FileNotFoundError, TimeoutError) as exc:
        console.print(f"[yellow]Agent run failed ({exc}). Defaults will be applied.[/yellow]")
        return
    merged = _merge_design_toml(model, result.stdout)
    if merged is None:
        console.print("[yellow]No parseable TOML returned — defaults will be applied.[/yellow]")
        return
    model = merged
    _write_scope(_scope_path(scope, root), _phases_to_dicts(model.phases), model.research, model.cyclic)
    console.print("Design merged into config. Run [bold]phases apply[/bold] to regenerate the AGTX plugin.")


@phases_app.command("apply")
def apply(scope: str = typer.Option("project", "--scope", help="project or global")) -> None:
    """Render plugin.toml + [agents] wiring, backup, diff, y/N write."""
    console = Console()
    root = git_root(Path.cwd()) if scope == "project" else None
    from ..config import load_config

    cfg = load_config(root)
    model = PhaseModel(research=cfg.workflow_research, cyclic=cfg.workflow_cyclic)
    model.phases = cfg.phases
    if not model.phases:
        model = PhaseModel.default()
    issues = [r for r in validate(model, registry()) if not r.ok]
    if issues:
        for i in issues:
            console.print(f"[red]{i.name}: {i.detail}[/red]")
        console.print("[red]Fix the model before applying.[/red]")
        raise SystemExit(1)

    from ..workflow.renderer import render_agents_config, render_plugin_toml

    plugin_path = _plugin_path(scope, root)
    backup = _backup(plugin_path)
    if backup:
        console.print(f"Backed up to {backup}")
    rendered = render_plugin_toml(model)
    plugin_path.parent.mkdir(parents=True, exist_ok=True)
    _write_with_diff(console, plugin_path, rendered)
    agents = render_agents_config(model)
    if agents:
        console.print("AGTX [agents] wiring to add to your agtx config.toml:")
        console.print("```toml\n[agents]\n" + "".join(f'{k} = "{v}"\n' for k, v in agents.items()) + "```")
    console.print("[green]Next: 'forgestack status' to check detection, then run AGTX.[/green]")


def _design_prompt(model: PhaseModel) -> str:
    lines = [
        "You are designing the ForgeStack workflow phase model. For EACH phase below, "
        "write (a) a one-paragraph 'purpose' and (b) a complete agent 'prompt' that starts "
        "with 'Task:\\n{task}' and guides that phase. Return ONLY a TOML fenced block:",
        "```toml",
        "[[workflow.phases]]",
        'key = "<key>"',
        'purpose = "..."',
        'prompt = """..."""',
        "```",
        "",
    ]
    for p in model.phases:
        lines.append(f"## phase key={p.key}" + (f" agent={p.agent}" if p.agent else ""))
        if p.team:
            lines.append("team (sprint-planning): " + ", ".join(p.team))
            lines.append("include role passes and a requirements × roles coverage matrix.")
        if p.skills:
            lines.append("available skills: " + ", ".join(p.skills))
        lines.append(f"current purpose: {p.purpose or '(none)'}")
    return "\n".join(lines)


def _merge_design_toml(model: PhaseModel, stdout: str) -> PhaseModel | None:
    block = _extract_toml(stdout)
    if block is None:
        return None
    import tomllib

    try:
        data = tomllib.loads(block)
    except Exception:
        return None
    phases = data.get("workflow", {}).get("phases")
    if not isinstance(phases, list):
        return None
    by_key = {p.key: p for p in model.phases}
    for item in phases:
        if not isinstance(item, dict):
            continue
        if item.get("key") in by_key:
            existing = by_key[item["key"]]
            if item.get("purpose") is not None:
                existing.purpose = str(item["purpose"])
            if item.get("prompt") is not None:
                existing.prompt = str(item["prompt"])
    return model


def _extract_toml(text: str) -> str | None:
    start = text.find("```toml")
    if start < 0:
        start = text.find("```\n[[workflow.phases]]")
    if start < 0:
        return None
    body = text[start:]
    body = body.split("```", 2)
    if len(body) < 2:
        return None
    return body[1] if body[1] else None


def _phases_to_dicts(phases: list[PhaseDef]) -> list[dict]:
    return [
        {
            **({"key": p.key}),
            **({"label": p.label} if p.label else {}),
            **({"purpose": p.purpose} if p.purpose else {}),
            **({"agent": p.agent} if p.agent else {}),
            **({"skills": p.skills} if p.skills else {}),
            **({"team": p.team} if p.team else {}),
            **({"artifact": p.artifact} if p.artifact else {}),
            **({"prompt": p.prompt} if p.prompt else {}),
        }
        for p in phases
    ]


def _agent_command(agent: str) -> list[str] | None:
    return _AGENT_CMDS.get(agent)


def _scope_path(scope: str, root: Path | None) -> Path:
    from ..paths import global_config_path, project_config_path

    if scope == "project" and root is not None:
        return project_config_path(root)
    return global_config_path()


def _plugin_path(scope: str, root: Path | None) -> Path:
    if scope == "project" and root is not None:
        base = root / ".agtx" / "plugins" / "forgestack"
    else:
        from ..paths import config_dir

        base = config_dir() / "agtx" / "plugins" / "forgestack"
    return base / "plugin.toml"


def _backup(path: Path) -> Path | None:
    if not path.exists():
        return None
    backup = path.with_suffix(path.suffix + ".bak")
    backup.write_text(path.read_text())
    return backup


def _write_with_diff(console: Console, path: Path, new: str) -> None:
    import difflib

    old = path.read_text() if path.exists() else ""
    if old == new:
        console.print("[green]plugin.toml unchanged.[/green]")
        return
    for line in difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm=""):
        console.print(line)
    if Confirm.ask("Write plugin.toml?"):
        path.write_text(new)
        console.print(f"Wrote {path}")
    else:
        console.print("Skipped.")
```

Note: `_deep_merge` on project scope merges into existing project config; global scope writes/overlays the merged global config. Existing `render_toml` round-trips all fields (incl. `[agents]`, `[integrations]`, `[runtime]`) because `Config.values` is re-emitted through the extended emitter in Task 2 — verify by running existing `tests/unit/test_config.py` after this task; if render_toml loses non-phase sections, extend it accordingly before the commit step.

- [ ] **Step 4: Register the group + setup delegation**

In `src/forgestack/cli.py`, add `from .commands import phases_cmd` to the existing `.commands` import block, and after the command registrations (or wherever the other command modules are registered):

```python
app.add_typer(phases_cmd.phases_app)
```

In `src/forgestack/commands/setup_cmd.py`, at the end of `cli()` (after the install prompt path), add:

```python
    from rich.prompt import Confirm

    if Confirm.ask("Design your workflow phases now? (forgestack phases)", default=False):
        from .phases_cmd import scaffold

        scaffold()
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/ -q`
Expected: PASS (all). Fix any `_fmt_kv` list-emission or render_toml regression before proceeding.

- [ ] **Step 6: Lint + commit**

Run: `.venv/bin/ruff check src/ && .venv/bin/ruff check tests/`
Then:

```bash
git add src/forgestack/commands/phases_cmd.py src/forgestack/cli.py src/forgestack/commands/setup_cmd.py tests/unit/test_phases_cmd.py
git commit -m "feat(phases): scaffold phase model via CLI wizard"
```

---

### Task 6: Phase-designer skill asset

**Files:**
- Create: `skills/forgestack/phase-designer/SKILL.md`
- Test: `tests/unit/test_phases_cmd.py` (assert the skill file exists and has the required frontmatter)

**Interfaces:**
- Consumes: nothing (product-owned skill).
- Produces: a discovery-visible `SKILL.md` with frontmatter `name: phase-designer` that the hypothetical agent companion reads so the `phases design` run shapes its output.

- [ ] **Step 1: Write the failing test** (append to `tests/unit/test_phases_cmd.py`)

```python
def test_phase_designer_skill_asset():
    from pathlib import Path

    skill = Path("skills/forgestack/phase-designer/SKILL.md")
    assert skill.exists()
    text = skill.read_text()
    assert text.startswith("---\nname: phase-designer")
    assert "coverage matrix" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/unit/test_phases_cmd.py::test_phase_designer_skill_asset -v`
Expected: FAIL (file missing)

- [ ] **Step 3: Create the skill**

`skills/forgestack/phase-designer/SKILL.md`:

```markdown
---
name: phase-designer
description: Write per-phase purpose and prompt content for a ForgeStack workflow phase model, preserving AGTX grammar.
---

Write the CONTENT of ForgeStack workflow phases (the model has already been scaffolded:
keys are fixed to research/planning/running/review/preresearch).

For each phase you are handed:

1. State the phase's `purpose` in one paragraph: what the agent in this phase must
   produce/decide, and what it must NOT do.
2. Write a complete `prompt` string that starts with `Task:\n{task}` and guides the
   phase agent: numbered Do items, explicit Do NOT items, and scoped acceptance-output
   expectations. Keep it prompt-token-lean; correctness over verbosity.
3. If the phase lists a `team` (planning only, opt-in): run one explicit role pass per
   member (deliverables, owned requirements, risks, commonly-overlooked items), delegate
   each pass to an internal sub-agent when the agent CLI supports it, and end with a
   requirements × roles COVERAGE MATRIX flagging uncovered requirements as gaps.
4. If the phase lists `skills`: reference them inside the prompt as opportunistically
   available discipline, never as vendored assets.

Return ONLY a fenced TOML block, one `[[workflow.phases]]` entry per phase, with `key`
matching the scaffolded key exactly. Do not invent new keys.
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/unit/test_phases_cmd.py::test_phase_designer_skill_asset -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add skills/forgestack/phase-designer/SKILL.md tests/unit/test_phases_cmd.py
git commit -m "feat(skills): add phase-designer companion skill"
```

---

### Task 7: `forgestack phases apply` integration + smoke coverage

**Files:**
- Modify: `src/forgestack/commands/phases_cmd.py` (apply already drafted in Task 5; this task hardens + tests it)
- Test: `tests/unit/test_phases_cmd.py`
- Test: `tests/smoke/test_cli.py` (append `phases --help` smoke)

**Interfaces:**
- Consumes: everything from Tasks 1-6.
- Produces: verified `apply` path (validate → backup → diff → y/N → write) and `design` fallback path.

- [ ] **Step 1: Write the failing tests** (append to `tests/unit/test_phases_cmd.py`)

```python
import pytest


def test_apply_skips_when_model_invalid(tmp_path, monkeypatch):
    from forgestack import paths
    from forgestack.commands.phases_cmd import apply

    proj = tmp_path / "proj"
    proj.mkdir()
    cfg_path = proj / ".forgestack.toml"
    cfg_path.write_text(
        '[workflow]\nresearch = true\ncyclic = false\n\n[[workflow.phases]]\n'
        'key = "populate"\n'
    )
    monkeypatch.setattr(paths, "project_config_path", lambda *a, **k: cfg_path)
    monkeypatch.setattr(paths, "git_root", lambda *a, **k: proj)
    monkeypatch.setattr("builtins.input", lambda *a, **k: "n")
    with pytest.raises(SystemExit):
        apply(scope="project")
    plugin = proj / ".agtx" / "plugins" / "forgestack" / "plugin.toml"
    assert not plugin.exists()


def test_apply_default_model_with_no_config(tmp_path, monkeypatch):
    # no project config -> default model -> plugin.toml gets written next to the agtx dir
    from forgestack import paths
    from forgestack.commands.phases_cmd import apply

    proj = tmp_path / "proj"
    proj.mkdir()
    monkeypatch.setattr(paths, "project_config_path", lambda *a, **k: proj / ".forgestack.toml")
    monkeypatch.setattr(paths, "git_root", lambda *a, **k: proj)
    monkeypatch.setattr("builtins.input", lambda *a, **k: "y")
    apply(scope="project")
    plugin = proj / ".agtx" / "plugins" / "forgestack" / "plugin.toml"
    assert plugin.exists()
    assert "cyclic = false" in plugin.read_text()
```

Note: `apply` as drafted uses `git_root(Path.cwd())` via `from ..paths import git_root` and builds `plugin_path` from it; these tests monkeypatch `paths.project_config_path`/`paths.git_root`, but `phases_cmd` imports `git_root` into its own namespace (`from ..paths import git_root`), so monkeypatching on `forgestack.paths` will not affect `phases_cmd.git_root`. **Adjust the implementation** so path lookups route through module-level indirection that tests can patch (e.g. import `from .. import paths` and call `paths.git_root` / `paths.project_config_path` inside functions), then the monkeypatches above work. Fix `_scope_path`/`_plugin_path`/`scaffold`/`design`/`apply` to call `paths.<fn>` so test patches take effect. Task 5's `_write_scope` already uses `Config.from_dict(merged)` correctly; do not reintroduce a module-level `from_dict` shim.

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/unit/test_phases_cmd.py -v`
Expected: FAIL (patch misses / unresolved names). Fix the indirection + shadowed import, rerun.

- [ ] **Step 3: Append the smoke test** to `tests/smoke/test_cli.py`

```python
def test_phases_smoke() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["phases", "--help"])
    assert result.exit_code == 0
    assert "scaffold" in result.stdout
```

- [ ] **Step 4: Run the full suite + lint**

Run: `.venv/bin/pytest tests/ -q && .venv/bin/ruff check src/ && .venv/bin/ruff check tests/`
Expected: all pass, ruff clean.

- [ ] **Step 5: Manual proof** — run in this repo as dry check (no write):

```bash
.venv/bin/python -c "
from forgestack.workflow.model import PhaseModel
from forgestack.workflow.renderer import render_plugin_toml, render_agents_config
m = PhaseModel.default()
out = render_plugin_toml(m)
print(out)
print('---agents---', render_agents_config(m))
"
```
Expected: prints the full plugin.toml then `---agents--- {}`.

- [ ] **Step 6: Commit**

```bash
git add src/forgestack/commands/phases_cmd.py tests/unit/test_phases_cmd.py tests/smoke/test_cli.py
git commit -m "feat(phases): harden apply/design paths with tests"
```

---

### Task 8: Docs

**Files:**
- Create: `docs/phases.md`
- Modify: `README.md` (add a line to the command table / quick start)
- Test: no new tests (doc only)

**Interfaces:**
- Consumes: the schema from Task 2, wizard flow from Tasks 5-7, constraint explainer from the spec §2/§6.

- [ ] **Step 1: Write `docs/phases.md`**

```markdown
# Workflow Phases

ForgeStack owns the workflow *model*: which phases exist, what each phase does, which agent
and skill packs it uses. AGTX remains the runtime authority — ForgeStack re-renders the AGTX
plugin from your config.

## Constraints (from AGTX)

- Board lanes are fixed: `backlog → planning → running → review → done`; research is an
  optional lane; Done/Backlog structural.
- Phase keys are limited to `research, planning, running, review, preresearch`.
- Per-phase agent routing is limited to those 4 named keys.
- A phase is reachable from Backlog only if its prompt/command contains `{task}`.

## Config

```toml
[workflow]
engine = "agtx"
research = true        # optional research lane
cyclic = false         # cyclic review -> planning

[[workflow.phases]]
key = "planning"
label = "Planning"
purpose = "Turn requirements into an implementation-ready contract."   # optional
agent = "codex"        # provider id from the adapter registry
skills = ["matt", "superpowers"]   # detected packs, referenced not vendored
team = []              # OPT-IN, disabled by default: planning-only sprint-planning roster
artifact = "plan.md"   # optional: docs/<plugin-name>/<file>
prompt = ""            # empty -> default template
```

Project `.forgestack.toml` phases replace the global list wholesale. When no phases are
configured, the current default model (research + planning + running + review) is used.

## Wizard

- `forgestack phases scaffold --scope project|global` — pick phases, research/cyclic, per
  phase agent + skill packs, and (planning, opt-in) a team roster. Deterministic.
- `forgestack phases design` — an agent fills per-phase purpose/prompt (reference
  `skills/forgestack/phase-designer`). Falls back to defaults when unavailable.
- `forgestack phases apply` — validates, backs up, diffs, then (on y/N) writes the AGTX
  `plugin.toml` and prints the `[agents]` wiring for your agtx config.toml.

## Multidisciplinary sprint-planning (planning `team`, opt-in)

When enabled, the planning agent runs one explicit role pass per team member and produces a
requirements × roles coverage matrix that flags requirements uncovered by the team — the
anti-missing/overlook mechanism. It costs extra tokens, so it is never enabled implicitly.
```

- [ ] **Step 2: README note** — in the command table section of `README.md`, after the `forgestack inbox` row, add:

```markdown
| `forgestack phases` | Design and apply the workflow phase model (scaffold → design → apply) |
```

- [ ] **Step 3: Run the full suite + lint**

Run: `.venv/bin/pytest tests/ -q && .venv/bin/ruff check src/ && .venv/bin/ruff check tests/`
Expected: all pass, ruff clean.

- [ ] **Step 4: Commit**

```bash
git add docs/phases.md README.md
git commit -m "docs(phases): document phase model and wizard"
```

---

## Self-Review (vs spec `docs/superpowers/specs/2026-09-02-customizable-phase-model-design.md`)

- **§4 data model**: `PhaseDef` includes key/label/purpose/agent/skills/team/artifact/prompt ✔ (Task 1, 2).
- **§4 default model**: research+planning+running+review with default prompts incl. ponytail paragraph ✔ (Task 1).
- **§5 render**: `render_plugin_toml` (cyclic/`[prompts]`/preresearch-as-`[commands]`/`[artifacts]`/skills paragraph/team sprint-planning paragraph) + `render_agents_config` 4-keys ✔ (Task 4).
- **§6 validation**: allowed keys, unique, planning+running+review, `{task}`, registry agent, unknown-skills warning → see Known gap below (Task 3).
- **§7 CLI**: scaffold/design/apply + setup delegation ✔ (Task 5, 7).
- **§7 design step**: subprocess agent launch (codex/claude/opencode) with TOML extraction + fallback ✔ (Task 5).
- **§8 tests**: golden render, team case, validate cases, cmd scaffold/apply mocks ✔ (Tasks 1,3,4,5,7).
- **§9 docs**: `docs/phases.md` ✔ (Task 8).
- **§10 non-goals**: no new lane names, AGTX stays authority, no per-phase agent outside 4 keys ✔.

**Known gap (Task 3)**: spec §6 lists "unknown skills → warning, not error". Skill-pack names are free-form strings (no catalog), so this is a no-op today. If a catalog is later added, extend `validate` with the `team:`-style warning pattern. Not blocking.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-09-02-customizable-phase-model.md`. Two execution options:

1. **Subagent-Driven (recommended)** — fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** — execute tasks in this session with checkpoints.

Which approach?