"""Tracker configuration without secrets."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TrackerConfig:
    provider: str = ""
    base_url: str = "https://api.plane.so"
    workspace_slug: str = ""
    project_id: str = ""
    project_identifier: str = ""
    api_key_env: str = "PLANE_API_KEY"

    @classmethod
    def from_dict(cls, data: object) -> TrackerConfig:
        if not isinstance(data, dict):
            return cls()
        return cls(
            provider=str(data.get("provider") or ""),
            base_url=str(data.get("base_url") or cls.base_url),
            workspace_slug=str(data.get("workspace_slug") or ""),
            project_id=str(data.get("project_id") or ""),
            project_identifier=str(data.get("project_identifier") or ""),
            api_key_env=str(data.get("api_key_env") or cls.api_key_env),
        )
