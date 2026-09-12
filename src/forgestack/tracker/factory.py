"""Construct the configured tracker provider."""

from __future__ import annotations

import os

from ..config import TrackerConfig
from .errors import TrackerConfigurationError
from .plane import PlaneClient


def build_tracker(config: TrackerConfig):
    provider = config.provider.strip().lower()
    if not provider:
        raise TrackerConfigurationError(
            "No tracker configured. Add [tracker] provider = \"plane\" to .forgestack.toml."
        )
    if provider != "plane":
        raise TrackerConfigurationError(
            f"Unsupported tracker provider '{config.provider}'. Plane is the only provider implemented."
        )
    missing = [
        name
        for name, value in (
            ("workspace_slug", config.workspace_slug),
            ("project_id", config.project_id),
            ("project_identifier", config.project_identifier),
        )
        if not value
    ]
    if missing:
        raise TrackerConfigurationError(
            "Plane tracker configuration is missing: " + ", ".join(missing)
        )
    api_key = os.environ.get(config.api_key_env)
    if not api_key:
        raise TrackerConfigurationError(
            f"Plane API key is missing from environment variable {config.api_key_env}."
        )
    return PlaneClient(
        base_url=config.base_url,
        workspace_slug=config.workspace_slug,
        project_id=config.project_id,
        project_identifier=config.project_identifier,
        api_key=api_key,
    )
