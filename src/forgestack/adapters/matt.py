"""Matt Pocock skills adapter — detection only; install via `npx skills install`."""

from __future__ import annotations

from pathlib import Path

from .protocol import Adapter, CheckResult, DetectResult, InstallMethod


class MattAdapter(Adapter):
    name = "matt"
    display_name = "Matt skills"
    category = "integrations"
    upstream_hint = "npx skills install mattpocock"

    def detect(self) -> DetectResult:
        sample = Path.home() / ".agents/skills/ask-matt"
        return DetectResult(sample.exists(), str(sample.parent), None)

    def is_compatible(self) -> bool | str:
        return True

    def recommended_install_method(self) -> InstallMethod:
        return InstallMethod("npm", ["npx", "skills", "install", "mattpocock"], self.upstream_hint)

    def generate_install_plan(self) -> list[str]:
        return ["npx skills install mattpocock"]

    def validate(self) -> list[CheckResult]:
        return [CheckResult("skills_dir", self.detect().installed, "~/.agents/skills")]
