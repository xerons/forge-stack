"""Adapter contract. Each external dependency implements this Protocol."""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from typing import Protocol


@dataclass
class DetectResult:
    installed: bool
    path: str | None = None
    version: str | None = None


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str = ""


@dataclass
class InstallMethod:
    backend: str  # brew | npm | pipx | curl-script | manual
    command: list[str] | None
    note: str = ""
    requires_approval: bool = True


@dataclass
class ToolInfo:
    name: str
    category: str
    required: bool = False
    upstream_hint: str | None = None


class Adapter(Protocol):
    name: str
    display_name: str
    category: str

    def detect(self) -> DetectResult: ...
    def is_compatible(self) -> bool | str: ...
    def recommended_install_method(self) -> InstallMethod: ...
    def generate_install_plan(self) -> list[str]: ...
    def validate(self) -> list[CheckResult]: ...
    def default_install_method_note(self) -> str:
        return getattr(self, "install_note", "")


def detect_version(
    command: str, version_flag: str = "--version"
) -> tuple[bool, str | None, str | None]:
    """Detect a CLI. Returns (installed, path, first semver found).

    Detection must never crash setup/doctor, so version-query failure still
    reports the tool as installed with version None.
    """
    path = shutil.which(command)
    if not path:
        return False, None, None
    try:
        out = subprocess.run(
            [path, version_flag], capture_output=True, text=True, timeout=5, check=False
        )
        first = out.stdout.strip().splitlines()[0] if out.stdout.strip() else ""
        m = re.search(r"\d+\.\d+\.\d+", first)
        return True, path, m.group(0) if m else None
    except (OSError, subprocess.SubprocessError, ValueError):
        return True, path, None
