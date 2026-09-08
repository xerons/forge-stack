from forgestack.workflow.model import PhaseDef, PhaseModel
from forgestack.workflow.renderer import render_agents_config, render_plugin_toml


def test_shipped_plugin_matches_generated_defaults():
    import tomllib

    from forgestack.assets import plugin_template

    shipped = tomllib.loads(plugin_template().read_text())
    generated = tomllib.loads(render_plugin_toml(PhaseModel.default()))
    assert shipped == generated


def test_render_default_plugin_toml_matches_current_contract():
    out = render_plugin_toml(PhaseModel.default())
    assert 'name = "forgestack"' in out
    assert "cyclic = false" in out
    assert "[prompts]" in out
    for key in ("research", "planning", "running", "review"):
        assert f"{key} = \"" in out
        assert "{task}" in out


def test_render_plugin_roundtrips_special_prompt_text():
    import tomllib

    m = PhaseModel.default()
    text = 'Task:\n{task}\nUse """quoted""" text and C:\\temp.\tEnd.'
    m.phases[1].prompt = text
    parsed = tomllib.loads(render_plugin_toml(m))
    assert parsed["prompts"]["planning"] == text


def test_render_plugin_skips_research_when_disabled():
    import tomllib

    m = PhaseModel.default()
    m.research = False
    parsed = tomllib.loads(render_plugin_toml(m))
    assert "research" not in parsed["prompts"]


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
