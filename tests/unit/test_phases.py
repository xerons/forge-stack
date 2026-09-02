from forgestack.workflow.model import (
    AGENT_PHASE_KEYS,
    ALLOWED_PHASE_KEYS,
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
