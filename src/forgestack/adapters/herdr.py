"""Herdr runtime adapter."""

from __future__ import annotations

from .protocol import Adapter, CheckResult, DetectResult, InstallMethod, detect_version


class HerdrAdapter(Adapter):
    name = "herdr"
    display_name = "Herdr"
    category = "runtime"

    def detect(self) -> DetectResult:
        return DetectResult(*detect_version("herdr"))

    def is_compatible(self) -> bool | str:
        return True

    def recommended_install_method(self) -> InstallMethod:
        return InstallMethod("brew", ["brew", "install", "herdr"], "Homebrew")

    def generate_install_plan(self) -> list[str]:
        return ["brew install herdr"]

    def validate(self) -> list[CheckResult]:
        return [CheckResult("detected", self.detect().installed, self.detect().version or "")]
