"""Phase model validation against the AGTX grammar and adapter registry."""

from __future__ import annotations

from collections.abc import Iterable

from ..adapters.protocol import CheckResult
from .model import ALLOWED_PHASE_KEYS, PhaseModel


def validate(model: PhaseModel, registry: Iterable) -> list[CheckResult]:
    results: list[CheckResult] = []
    keys = [p.key for p in model.phases]

    for p in model.phases:
        if p.key not in ALLOWED_PHASE_KEYS:
            results.append(
                CheckResult(
                    f"phase {p.key}",
                    False,
                    f"not in allowed keys {sorted(ALLOWED_PHASE_KEYS)}",
                )
            )

    dupes = sorted({k for k in keys if keys.count(k) > 1})
    if dupes:
        results.append(CheckResult("unique keys", False, ", ".join(dupes)))

    for required in ("planning", "running", "review"):
        if required not in keys:
            results.append(CheckResult(required, False, "required phase missing"))

    has_research = "research" in keys
    if model.research != has_research:
        configured = "enabled" if model.research else "disabled"
        present = "present" if has_research else "absent"
        results.append(
            CheckResult(
                "research configuration",
                True,
                f"warning: research is {configured} but the phase is {present}; rendering follows the flag",
            )
        )

    if not any("{task}" in (p.prompt or "") for p in model.phases):
        results.append(CheckResult("reachable", False, "no prompt contains {task}"))

    known = {getattr(a, "name", "") for a in registry}
    for p in model.phases:
        if p.agent and p.agent not in known:
            results.append(CheckResult(f"agent:{p.key}", False, f"{p.agent} not in registry"))

    for p in model.phases:
        if p.team and p.key != "planning":
            results.append(CheckResult(f"team:{p.key}", True, "team ignored outside planning"))

    return results
