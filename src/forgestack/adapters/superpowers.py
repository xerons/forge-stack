"""Superpowers adapter — detection/fallback via equivalent discipline."""

from __future__ import annotations

from pathlib import Path

from .protocol import Adapter, CheckResult, DetectResult, InstallMethod


class SuperpowersAdapter(Adapter):
    name = "superpowers"
    display_name = "Superpowers"
    category = "integrations"
    upstream_hint = "npx skills install superpowers"

    def detect(self) -> DetectResult:
        opencode_path = Path.home() / ".cache/opencode/packages/superpowers@git+https:/"
        return DetectResult(opencode_path.exists(), str(opencode_path.parent), None)

    def is_compatible(self) -> bool | str:
        return True

    def recommended_install_method(self) -> InstallMethod:
        return InstallMethod("npm", ["npx", "skills", "install", "superpowers"], self.upstream_hint)

    def generate_install_plan(self) -> list[str]:
        return ["npx skills install superpowers"]

    def validate(self) -> list[CheckResult]:
        return [CheckResult("detected", self.detect().installed, "fallback: discipline check")]
