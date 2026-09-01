"""Unit tests for paths module."""

from pathlib import Path

from forgestack.paths import config_dir, git_root, global_config_path, project_config_path


def test_global_config_path_uses_env() -> None:
    env = {"XDG_CONFIG_HOME": "/tmp/forgestack-test"}
    assert global_config_path(env) == Path("/tmp/forgestack-test/forgestack/config.toml")


def test_config_dir() -> None:
    env = {"XDG_CONFIG_HOME": "/tmp/forgestack-test"}
    assert config_dir(env) == Path("/tmp/forgestack-test/forgestack")


def test_project_config_path(tmp_path: Path) -> None:
    assert project_config_path(tmp_path) == tmp_path / ".forgestack.toml"


def test_git_root_finds_upward(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    nested = tmp_path / "a" / "b"
    nested.mkdir(parents=True)
    assert git_root(nested) == tmp_path


def test_git_root_none_when_missing(tmp_path: Path) -> None:
    assert git_root(tmp_path) is None
