"""AGTX adapter — workflow authority."""

from __future__ import annotations

from .protocol import Adapter, CheckResult, DetectResult, InstallMethod, detect_version

AGTX_IDENTIFIER = "agtx"
PLUGIN_NAME = "forgestack"


class AgtxAdapter(Adapter):
    name = AGTX_IDENTIFIER
    display_name = "AGTX (workflow)"
    category = "workflow"
    required = True
    upstream_hint = "via official AGTX installer (see README) — never vendor"

    def detect(self) -> DetectResult:
        return DetectResult(*detect_version("agtx"))

    def is_compatible(self) -> bool | str:
        v = self.detect().version
        if v is None:
            return "unknown"
        major = int(v.split(".")[0]) if v else 0
        return 1 <= major < 2

    def recommended_install_method(self) -> InstallMethod:
        return InstallMethod("manual", None, "install via AGTX official docs")

    def generate_install_plan(self) -> list[str]:
        return ["echo 'see AGTX official installation docs'"]

    def validate(self) -> list[CheckResult]:
        return [
            CheckResult("detected", self.detect().installed, self.display_name),
            CheckResult("version", self.is_compatible() is True, self.detect().version or ""),
        ]
