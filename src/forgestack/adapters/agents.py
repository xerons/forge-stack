"""Agent CLI adapter factory — provider-agnostic, all optional."""

from __future__ import annotations

import re
import shutil
import subprocess
from .protocol import Adapter, CheckResult, DetectResult, InstallMethod


def make_agent_adapter(name: str, hint: str, category: str = "agents"):
    class AgentAdapter(Adapter):
        def __init__(s) -> None:
            s.name = name
            s.display_name = f"Agent CLI: {name}"
            s.category = category
            s.install_hint = hint

        def detect(self) -> DetectResult:
            path = shutil.which(name)
            if not path:
                return DetectResult(False)
            try:
                out = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=5)
                first = out.stdout.strip().splitlines()[0] if out.stdout.strip() else ""
                v = re.search(r"\d+\.\d+\.\d+", first)
                return DetectResult(True, path, v.group(0) if v else None)
            except Exception:
                return DetectResult(True, path, None)

        def is_compatible(self) -> bool | str:
            return True

        def recommended_install_method(self) -> InstallMethod:
            return InstallMethod(
                "manual",
                None,
                f"upstream hint: {self.install_hint}",
                requires_approval=True,
            )

        def generate_install_plan(self) -> list[str]:
            return [f"echo '{self.install_hint}'"]

        def validate(self) -> list[CheckResult]:
            d = self.detect()
            return [CheckResult("detected", d.installed, d.path or "missing")]

    return AgentAdapter()
