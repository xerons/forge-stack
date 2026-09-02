"""ponytail adapter — lazy senior-dev discipline, detection only (like Superpowers)."""

from __future__ import annotations

from pathlib import Path

from .protocol import Adapter, CheckResult, DetectResult, InstallMethod

_CACHE = Path.home() / ".cache/opencode/packages/@dietrichgebert/ponytail@latest"
_SKILL_DIR = Path.home() / ".agents/skills/ponytail"
_PROJECT_PLUGIN = Path(".opencode/plugins/ponytail.mjs")


class PonytailAdapter(Adapter):
    name = "ponytail"
    display_name = "ponytail discipline"
    category = "integrations"
    required = False
    upstream_hint = "add @dietrichgebert/ponytail to opencode.json plugins (see upstream repo)"

    def detect(self) -> DetectResult:
        paths = [p for p in (_CACHE, _SKILL_DIR, _PROJECT_PLUGIN) if p.exists()]
        return DetectResult(bool(paths), str(paths[0].parent) if paths else None, None)

    def is_compatible(self) -> bool | str:
        return True

    def recommended_install_method(self) -> InstallMethod:
        return InstallMethod("manual", None, self.upstream_hint)

    def generate_install_plan(self) -> list[str]:
        return ["add '@dietrichgebert/ponytail' to opencode.json plugins"]

    def validate(self) -> list[CheckResult]:
        return [CheckResult("detected", self.detect().installed, "running-phase discipline")]