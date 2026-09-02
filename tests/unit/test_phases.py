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


from forgestack.config import Config, load_config, render_toml  # noqa: F401


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
