"""Herdr runtime adapter."""

from __future__ import annotations

import re
import shutil
import subprocess

from .protocol import Adapter, CheckResult, DetectResult, InstallMethod


class HerdrAdapter(Adapter):
    name = "herdr"
    display_name = "Herdr"
    category = "runtime"

    def detect(self) -> DetectResult:
        path = shutil.which("herdr")
        if not path:
            return DetectResult(False)
        try:
            out = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=5)
            first = out.stdout.strip()
            m = re.search(r"\d+\.\d+\.\d+", first)
            return DetectResult(True, path, m.group(0) if m else None)
        except Exception:
            return DetectResult(True, path, None)

    def is_compatible(self) -> bool | str:
        return True

    def recommended_install_method(self) -> InstallMethod:
        return InstallMethod("brew", ["brew", "install", "herdr"], "Homebrew")

    def generate_install_plan(self) -> list[str]:
        return ["brew install herdr"]

    def validate(self) -> list[CheckResult]:
        return [CheckResult("detected", self.detect().installed, self.detect().version or "")]
