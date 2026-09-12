"""Non-mutating tracker configuration diagnostics."""

from __future__ import annotations

import os

from ..adapters.protocol import CheckResult
from .config import TrackerConfig


def checks(config: TrackerConfig) -> list[CheckResult]:
    """Report local tracker readiness without making a network request."""
    if not config.provider:
        return [CheckResult("tracker", True, "not configured")]
    if config.provider.casefold() != "plane":
        return [CheckResult("tracker provider", False, f"unsupported provider: {config.provider}")]

    return [
        CheckResult("tracker provider", True, "plane"),
        CheckResult(
            "tracker project configuration",
            bool(config.workspace_slug and config.project_id and config.project_identifier),
            "workspace, project UUID, and project identifier are required",
        ),
        CheckResult(
            "tracker API key",
            bool(os.environ.get(config.api_key_env)),
            f"environment variable: {config.api_key_env}",
        ),
    ]
