"""code-server adapter — optional UX."""

from __future__ import annotations

import shutil

from .protocol import Adapter, CheckResult, DetectResult, InstallMethod


class CodeServerAdapter(Adapter):
    name = "code-server"
    display_name = "code-server"
    category = "runtime"

    def detect(self) -> DetectResult:
        return DetectResult(bool(shutil.which("code-server")), shutil.which("code-server"), None)

    def is_compatible(self) -> bool | str:
        return True

    def recommended_install_method(self) -> InstallMethod:
        return InstallMethod("brew", ["brew", "install", "code-server"], "Homebrew")

    def generate_install_plan(self) -> list[str]:
        return ["brew install code-server"]

    def validate(self) -> list[CheckResult]:
        return [CheckResult("detected", self.detect().installed, "optional")]
