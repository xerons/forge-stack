"""Adapter contract. Each external dependency implements this Protocol."""

from __future__ import annotations

from dataclasses import dataclass, field
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
