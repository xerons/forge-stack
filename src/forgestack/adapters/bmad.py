"""BMAD adapter — project-scoped detection of `_bmad/` directory."""

from __future__ import annotations

from pathlib import Path

from .protocol import Adapter, CheckResult, DetectResult, InstallMethod


class BmadAdapter(Adapter):
    name = "bmad"
    display_name = "BMAD"
    category = "integrations"
    upstream_hint = "npx bmad-method install"

    def __init__(self, project_root: Path | None = None) -> None:
        self._root = project_root

    def detect(self) -> DetectResult:
        if self._root is None:
            return DetectResult(False, None, None)
        bmad_dir = Path(self._root) / "_bmad"
        return DetectResult(bmad_dir.exists(), str(bmad_dir), None)

    def is_compatible(self) -> bool | str:
        return True

    def recommended_install_method(self) -> InstallMethod:
        return InstallMethod("npm", ["npx", "bmad-method", "install"], self.upstream_hint)

    def generate_install_plan(self) -> list[str]:
        return ["npx bmad-method install"]

    def validate(self) -> list[CheckResult]:
        return [CheckResult("project_scoped_bmad_dir", bool(self.detect().installed), "_bmad/")]
