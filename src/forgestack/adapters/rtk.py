"""RTK adapter — opportunistic token reduction. Detection-only, never stacked aggressively."""

from __future__ import annotations

from .protocol import Adapter, CheckResult, DetectResult, InstallMethod, detect_version


class RtkAdapter(Adapter):
    name = "rtk"
    display_name = "RTK"
    category = "integrations"

    def detect(self) -> DetectResult:
        return DetectResult(*detect_version("rtk"))

    def is_compatible(self) -> bool | str:
        return True

    def recommended_install_method(self) -> InstallMethod:
        return InstallMethod("brew", ["brew", "install", "rtk"], "Homebrew")

    def generate_install_plan(self) -> list[str]:
        return ["brew install rtk"]

    def validate(self) -> list[CheckResult]:
        return [CheckResult("detected", self.detect().installed, self.detect().version or "")]
