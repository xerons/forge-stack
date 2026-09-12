"""Provider-neutral tracker records and operations used by ForgeStack."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class TrackerState:
    id: str
    name: str
    group: str = ""


@dataclass(frozen=True)
class TrackerWorkItem:
    id: str
    identifier: str
    name: str
    state_id: str
    state_name: str
    state_group: str
    project_id: str
    parent_id: str | None = None
    module_id: str | None = None
    description_html: str = ""
    raw: Mapping[str, Any] = field(default_factory=dict, repr=False)


class TrackerProvider(Protocol):
    """The small tracker surface required by the first Orchestrator slice."""

    def list_states(self) -> list[TrackerState]: ...

    def get_work_item(self, identifier: str) -> TrackerWorkItem: ...

    def update_work_item(
        self,
        work_item_id: str,
        *,
        state_id: str | None = None,
        parent_id: str | None = None,
        module_id: str | None = None,
    ) -> TrackerWorkItem: ...

    def create_work_item(
        self,
        *,
        name: str,
        description_html: str = "",
        state_id: str | None = None,
        parent_id: str | None = None,
        module_id: str | None = None,
    ) -> TrackerWorkItem: ...

    def add_comment(self, work_item_id: str, comment_html: str) -> None: ...
