"""Unit tests for agents_cmd — regression: routing writes must not clobber phases."""

import tomllib

from forgestack import paths
from forgestack.commands import agents_cmd


def _seed_global_config(path) -> None:
    from forgestack.managed import write_managed

    path.parent.mkdir(parents=True, exist_ok=True)
    write_managed(
        path,
        path.parent,
        '''profile = "default"

[manager]
agent = "codex"

[workflow]
engine = "agtx"
research = false
cyclic = true

[[workflow.phases]]
key = "planning"
agent = "codex"

[[workflow.phases]]
key = "running"
agent = "opencode"

[agents]
research = "codex"
planning = "codex"
running = "codex"
review = "codex"

[integrations]
herdr = true
''',
        source="config.toml",
    )


def _run_agents_cli(tmp_path, monkeypatch):
    cfg_path = tmp_path / "global" / "config.toml"
    _seed_global_config(cfg_path)
    # git_root -> tmp_path: project config absent, so load_config reads only the seeded global.
    # config.py and agents_cmd bind global_config_path by direct import, so patch
    # every module namespace that holds a reference.
    import forgestack.config as config_mod

    fake_global = lambda *a, **k: cfg_path
    monkeypatch.setattr(paths, "global_config_path", fake_global)
    monkeypatch.setattr(config_mod, "global_config_path", fake_global)
    monkeypatch.setattr(paths, "git_root", lambda *a, **k: tmp_path)
    answers = iter(["claude", "gemini", "opencode", "agy"])
    monkeypatch.setattr(
        agents_cmd.Prompt, "ask", staticmethod(lambda *a, **k: next(answers))
    )
    agents_cmd.cli()
    return tomllib.loads(cfg_path.read_text())


def test_agents_preserves_phases_and_values(tmp_path, monkeypatch):
    data = _run_agents_cli(tmp_path, monkeypatch)
    wf = data["workflow"]
    assert wf["research"] is False
    assert wf["cyclic"] is True
    assert [p["key"] for p in wf["phases"]] == ["planning", "running"]
    assert data["integrations"]["herdr"] is True
    assert data["manager"]["agent"] == "codex"


def test_agents_writes_agents_roles(tmp_path, monkeypatch):
    data = _run_agents_cli(tmp_path, monkeypatch)
    assert data["agents"] == {
        "research": "claude",
        "planning": "gemini",
        "running": "opencode",
        "review": "agy",
    }
