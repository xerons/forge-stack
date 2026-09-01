"""Agent CLI adapter factory — provider-agnostic, all optional."""

from __future__ import annotations

from .protocol import Adapter, CheckResult, DetectResult, InstallMethod, detect_version


def make_agent_adapter(name: str, hint: str, category: str = "agents"):
    class AgentAdapter(Adapter):
        def __init__(s) -> None:
            s.name = name
            s.display_name = f"Agent CLI: {name}"
            s.category = category
            s.install_hint = hint

        def detect(self) -> DetectResult:
            return DetectResult(*detect_version(name))

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
