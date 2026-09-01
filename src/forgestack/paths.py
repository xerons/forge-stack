"""Filesystem path helpers for ForgeStack."""

from __future__ import annotations

import os
from pathlib import Path

APP_NAME = "forgestack"


def global_config_path(env: dict | None = None) -> Path:
    e = env or os.environ
    return Path(e.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))) / APP_NAME / "config.toml"


def config_dir(env: dict | None = None) -> Path:
    return global_config_path(env).parent


def project_config_path(root: Path) -> Path:
    return root / f".{APP_NAME}.toml"


def git_root(start: Path) -> Path | None:
    cur = start.resolve()
    for candidate in [cur, *cur.parents]:
        if (candidate / ".git").exists():
            return candidate
    return None
