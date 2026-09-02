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
