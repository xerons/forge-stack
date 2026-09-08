from types import SimpleNamespace

from forgestack.commands import manager_cmd


def test_manager_command_uses_codex_interactive_prompt(tmp_path, monkeypatch):
    monkeypatch.setattr(manager_cmd.shutil, "which", lambda name: "/bin/" + name)
    command = manager_cmd._manager_command("codex", tmp_path, "manager instructions")
    assert command == ["codex", "-C", str(tmp_path), "manager instructions"]


def test_manager_command_returns_none_for_unknown_provider(tmp_path, monkeypatch):
    monkeypatch.setattr(manager_cmd.shutil, "which", lambda name: "/bin/" + name)
    assert manager_cmd._manager_command("unknown", tmp_path, "instructions") is None


def test_manager_cli_launches_configured_agent(tmp_path, monkeypatch):
    monkeypatch.setattr(manager_cmd, "git_root", lambda _: tmp_path)
    monkeypatch.setattr(manager_cmd, "registry", list)
    monkeypatch.setattr(manager_cmd, "load_config", lambda _: SimpleNamespace(manager_agent="codex"))
    monkeypatch.setattr(manager_cmd.shutil, "which", lambda name: "/bin/" + name)
    calls = []
    monkeypatch.setattr(
        manager_cmd.subprocess,
        "run",
        lambda command, cwd, check: calls.append((command, cwd, check)) or SimpleNamespace(returncode=0),
    )

    assert manager_cmd.cli() == 0
    assert calls and calls[0][0][:3] == ["codex", "-C", str(tmp_path)]
    assert calls[0][1] == tmp_path


def test_manager_cli_reports_nonzero_launch(tmp_path, monkeypatch):
    monkeypatch.setattr(manager_cmd, "git_root", lambda _: tmp_path)
    monkeypatch.setattr(manager_cmd, "registry", list)
    monkeypatch.setattr(manager_cmd, "load_config", lambda _: SimpleNamespace(manager_agent="codex"))
    monkeypatch.setattr(manager_cmd.shutil, "which", lambda name: "/bin/" + name)
    monkeypatch.setattr(
        manager_cmd.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=7),
    )
    assert manager_cmd.cli() == 7


def test_manager_cli_requires_confirmation_for_project_agent_override(tmp_path, monkeypatch):
    monkeypatch.setattr(manager_cmd, "git_root", lambda _: tmp_path)
    monkeypatch.setattr(manager_cmd, "registry", list)
    configs = iter(
        [
            SimpleNamespace(manager_agent="gemini"),
            SimpleNamespace(manager_agent="codex"),
        ]
    )
    monkeypatch.setattr(manager_cmd, "load_config", lambda _: next(configs))
    monkeypatch.setattr(manager_cmd.Confirm, "ask", lambda *args, **kwargs: False)
    monkeypatch.setattr(manager_cmd.shutil, "which", lambda name: "/bin/" + name)

    def unexpected_run(*args, **kwargs):
        raise AssertionError("the project override should not launch without confirmation")

    monkeypatch.setattr(manager_cmd.subprocess, "run", unexpected_run)
    assert manager_cmd.cli() == 1
