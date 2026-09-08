"""Unit tests for config module."""

from pathlib import Path

from forgestack.config import Config, load_config, render_toml


def test_load_config_with_existing_file(tmp_path: Path) -> None:
    config_file = tmp_path / ".forgestack.toml"
    config_file.write_text("""
profile = "default"

[manager]
agent = "codex"

[agents]
research = "codex"
planning = "codex"
running = "codex"
review = "codex"
""")
    cfg = load_config(tmp_path)
    assert cfg.profile == "default"
    assert cfg.manager_agent == "codex"
    assert cfg.agents["research"] == "codex"


def test_load_config_with_missing_file(tmp_path: Path) -> None:
    cfg = load_config(tmp_path)
    assert cfg.profile == "default"
    assert cfg.agents == {}


def test_render_toml_roundtrip() -> None:
    cfg = Config(profile="test", manager_agent="codex", agents={"running": "opencode"})
    rendered = render_toml(cfg)
    assert "profile = \"test\"" in rendered
    assert "running = \"opencode\"" in rendered


def test_render_toml_roundtrips_special_phase_text() -> None:
    import tomllib

    text = 'Task:\n{task}\nUse """quoted""" text and C:\\temp.\tEnd.'
    cfg = Config.from_dict(
        {
            "workflow": {
                "phases": [
                    {"key": "planning", "purpose": text, "prompt": text},
                    {"key": "running", "prompt": "Task:\n{task}"},
                    {"key": "review", "prompt": "Task:\n{task}"},
                ]
            }
        }
    )
    parsed = tomllib.loads(render_toml(cfg))
    phase = parsed["workflow"]["phases"][0]
    assert phase["purpose"] == text
    assert phase["prompt"] == text
