"""AGTX adapter — workflow authority."""

from __future__ import annotations

from .protocol import Adapter, CheckResult, DetectResult, InstallMethod

AGTX_IDENTIFIER = "agtx"
PLUGIN_NAME = "forgestack"


class AgtxAdapter(Adapter):
    name = AGTX_IDENTIFIER
    display_name = "AGTX (workflow)"
    category = "workflow"
    required = True
    upstream_hint = "via official AGTX installer (see README) — never vendor"

    def detect(self) -> DetectResult:
        return DetectResult(*_detect("agtx", "--version"))

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


def _detect(cmd: str, version_flag: str) -> tuple[bool, str | None, str | None]:
    import shutil
    import subprocess

    path = shutil.which(cmd)
    if not path:
        return False, None, None
    try:
        out = subprocess.run([path, version_flag], capture_output=True, text=True, timeout=5)
        first = out.stdout.strip().splitlines()[0] if out.stdout.strip() else ""
        version = _first_version(first)
        return True, path, version
    except Exception:
        return True, path, None


def _first_version(text: str) -> str | None:
    import re

    m = re.search(r"\d+\.\d+\.\d+", text)
    return m.group(0) if m else None
