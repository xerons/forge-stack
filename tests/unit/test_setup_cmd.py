"""Tests for forgestack.commands.setup_cmd — asset installation stage."""

from pathlib import Path
from unittest.mock import patch

from forgestack.assets import asset_root, skill_suite_files
from forgestack.commands.setup_cmd import _install_assets

Base = asset_root()
Assets = Base / "skills"
SkillFiles = skill_suite_files()


def _make_console():
    from rich.console import Console

    return Console(file=Path("/dev/null").open("w"))


def _rel(path: Path) -> str:
    return str(path.relative_to(Assets))


def _patch_confirm():
    return patch("forgestack.commands.setup_cmd.Confirm.ask", side_effect=[True])


def test_global_scope(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "forgestack.commands.setup_cmd._user_agents_dir",
        lambda: tmp_path / ".agents",
    )
    monkeypatch.setattr(
        "forgestack.paths.config_dir",
        lambda **_: tmp_path / ".config" / "forgestack",
    )
    with _patch_confirm():
        _install_assets("global", _make_console())

    for f in SkillFiles:
        target = tmp_path / ".agents" / "skills" / _rel(f)
        assert target.exists(), f"missing: {target}"

    plugin_target = (
        tmp_path / ".config" / "forgestack" / "agtx" / "plugins" / "forgestack" / "plugin.toml"
    )
    assert plugin_target.exists()


def test_project_scope(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()

    monkeypatch.chdir(repo)
    monkeypatch.setattr(
        "forgestack.commands.setup_cmd.paths.git_root",
        lambda _cwd: repo,
    )
    with _patch_confirm():
        _install_assets("project", _make_console())

    for f in SkillFiles:
        target = repo / ".agents" / "skills" / _rel(f)
        assert target.exists(), f"missing: {target}"

    plugin_target = repo / ".agtx" / "plugins" / "forgestack" / "plugin.toml"
    assert plugin_target.exists()


def test_user_modified_skill(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "forgestack.commands.setup_cmd._user_agents_dir",
        lambda: tmp_path / ".agents",
    )
    monkeypatch.setattr(
        "forgestack.paths.config_dir",
        lambda **_: tmp_path / ".config" / "forgestack",
    )
    with _patch_confirm():
        _install_assets("global", _make_console())

    target = tmp_path / ".agents" / "skills" / "forgestack" / "SKILL.md"
    target.write_text("user edit\n", encoding="utf-8")

    with _patch_confirm():
        _install_assets("global", _make_console())

    assert target.read_text(encoding="utf-8") == "user edit\n"


def test_foreign_file_preserved(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "forgestack.commands.setup_cmd._user_agents_dir",
        lambda: tmp_path / ".agents",
    )
    monkeypatch.setattr(
        "forgestack.paths.config_dir",
        lambda **_: tmp_path / ".config" / "forgestack",
    )

    foreign = tmp_path / ".agents" / "skills" / "forgestack" / "custom.md"
    foreign.parent.mkdir(parents=True)
    foreign.write_text("foreign\n", encoding="utf-8")

    with _patch_confirm():
        _install_assets("global", _make_console())

    assert foreign.read_text(encoding="utf-8") == "foreign\n"


def test_second_run_idempotent(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "forgestack.commands.setup_cmd._user_agents_dir",
        lambda: tmp_path / ".agents",
    )
    monkeypatch.setattr(
        "forgestack.paths.config_dir",
        lambda **_: tmp_path / ".config" / "forgestack",
    )
    with _patch_confirm():
        _install_assets("global", _make_console())
    contents1 = {
        str(p): p.read_bytes()
        for p in (tmp_path / ".agents").rglob("*")
        if p.is_file()
    }

    with _patch_confirm():
        _install_assets("global", _make_console())
    contents2 = {
        str(p): p.read_bytes()
        for p in (tmp_path / ".agents").rglob("*")
        if p.is_file()
    }

    assert contents1 == contents2
