"""Plane REST provider using the current work-items API."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from .errors import TrackerNotFoundError, TrackerRequestError
from .protocol import TrackerState, TrackerWorkItem

_Opener = Callable[..., Any]


class PlaneClient:
    """Small Plane client for deterministic Orchestrator operations.

    The API key is passed explicitly so callers can source it from an
    environment variable without ever putting it in project configuration.
    ``opener`` is injectable for unit tests.
    """

    def __init__(
        self,
        *,
        base_url: str,
        workspace_slug: str,
        project_id: str,
        project_identifier: str,
        api_key: str,
        timeout: float = 15.0,
        opener: _Opener | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.workspace_slug = workspace_slug
        self.project_id = project_id
        self.project_identifier = project_identifier
        self.api_key = api_key
        self.timeout = timeout
        self._opener = opener or urlopen

    def list_states(self) -> list[TrackerState]:
        payload = self._request("GET", self._project_path("states/"))
        return [
            TrackerState(
                id=str(item.get("id", "")),
                name=str(item.get("name", "")),
                group=str(item.get("group", "")),
            )
            for item in _results(payload)
            if item.get("id")
        ]

    def get_work_item(self, identifier: str) -> TrackerWorkItem:
        if _looks_like_uuid(identifier):
            path = self._project_path(f"work-items/{quote(identifier, safe='')}/")
        else:
            path = self._workspace_path(f"work-items/{quote(identifier, safe='')}/")
        payload = self._request("GET", path, query={"expand": "state,module"})
        item = self._parse_work_item(payload)
        if not item.id:
            raise TrackerNotFoundError(f"Plane work item '{identifier}' was not found")
        if not item.state_name and item.state_id:
            item = self._with_state_name(item)
        return item

    def update_work_item(
        self,
        work_item_id: str,
        *,
        state_id: str | None = None,
        parent_id: str | None = None,
        module_id: str | None = None,
    ) -> TrackerWorkItem:
        data: dict[str, str] = {}
        if state_id is not None:
            data["state"] = state_id
        if parent_id is not None:
            data["parent"] = parent_id
        if module_id is not None:
            data["module"] = module_id
        payload = self._request(
            "PATCH",
            self._project_path(f"work-items/{quote(work_item_id, safe='')}/"),
            body=data,
        )
        item = self._parse_work_item(payload)
        if not item.id:
            raise TrackerNotFoundError(f"Plane work item '{work_item_id}' was not returned")
        if not item.state_name and item.state_id:
            item = self._with_state_name(item)
        return item

    def create_work_item(
        self,
        *,
        name: str,
        description_html: str = "",
        state_id: str | None = None,
        parent_id: str | None = None,
        module_id: str | None = None,
    ) -> TrackerWorkItem:
        data: dict[str, str] = {"name": name}
        if description_html:
            data["description_html"] = description_html
        if state_id is not None:
            data["state"] = state_id
        if parent_id is not None:
            data["parent"] = parent_id
        if module_id is not None:
            data["module"] = module_id
        payload = self._request("POST", self._project_path("work-items/"), body=data)
        item = self._parse_work_item(payload)
        if not item.id:
            raise TrackerRequestError(None, "Plane did not return the created work item")
        if not item.state_name and item.state_id:
            item = self._with_state_name(item)
        return item

    def add_comment(self, work_item_id: str, comment_html: str) -> None:
        self._request(
            "POST",
            self._project_path(f"work-items/{quote(work_item_id, safe='')}/comments/"),
            body={"comment_html": comment_html, "access": "INTERNAL"},
        )

    def _with_state_name(self, item: TrackerWorkItem) -> TrackerWorkItem:
        states = {state.id: state for state in self.list_states()}
        state = states.get(item.state_id)
        if state is None:
            return item
        return TrackerWorkItem(
            **{
                **item.__dict__,
                "state_name": state.name,
                "state_group": state.group,
            }
        )

    def _parse_work_item(self, data: Mapping[str, Any]) -> TrackerWorkItem:
        state = data.get("state")
        state_id = str(state.get("id", "")) if isinstance(state, Mapping) else str(state or "")
        state_name = str(state.get("name", "")) if isinstance(state, Mapping) else str(data.get("state_name", ""))
        state_group = str(state.get("group", "")) if isinstance(state, Mapping) else str(data.get("state_group", ""))
        module = data.get("module")
        module_id = str(module.get("id", "")) if isinstance(module, Mapping) else str(module or "")
        project = data.get("project")
        project_id = str(project.get("id", "")) if isinstance(project, Mapping) else str(project or self.project_id)
        sequence_id = data.get("sequence_id")
        identifier = str(data.get("identifier") or "")
        if not identifier and sequence_id is not None:
            identifier = f"{self.project_identifier}-{sequence_id}"
        return TrackerWorkItem(
            id=str(data.get("id", "")),
            identifier=identifier,
            name=str(data.get("name", "")),
            state_id=state_id,
            state_name=state_name,
            state_group=state_group,
            project_id=project_id,
            parent_id=_optional_id(data.get("parent")),
            module_id=module_id or None,
            description_html=str(data.get("description_html") or ""),
            raw=data,
        )

    def _project_path(self, suffix: str) -> str:
        return self._workspace_path(f"projects/{quote(self.project_id, safe='')}/{suffix}")

    def _workspace_path(self, suffix: str) -> str:
        return f"/api/v1/workspaces/{quote(self.workspace_slug, safe='')}/{suffix}"

    def _request(
        self,
        method: str,
        path: str,
        *,
        query: Mapping[str, str] | None = None,
        body: Mapping[str, Any] | None = None,
    ) -> Mapping[str, Any] | list[Any]:
        url = self.base_url + path
        if query:
            url += "?" + urlencode(query)
        encoded = json.dumps(body).encode("utf-8") if body is not None else None
        request = Request(
            url,
            data=encoded,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-API-Key": self.api_key,
            },
            method=method,
        )
        try:
            response = self._opener(request, timeout=self.timeout)
            try:
                raw = response.read()
            finally:
                close = getattr(response, "close", None)
                if close is not None:
                    close()
        except HTTPError as exc:
            detail = _response_detail(exc)
            raise TrackerRequestError(exc.code, detail) from exc
        except URLError as exc:
            raise TrackerRequestError(None, str(exc.reason)) from exc
        except OSError as exc:
            raise TrackerRequestError(None, str(exc)) from exc

        if not raw:
            return {}
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise TrackerRequestError(None, "Plane returned invalid JSON") from exc
        if not isinstance(payload, (dict, list)):
            raise TrackerRequestError(None, "Plane returned an unexpected JSON value")
        return payload


def _results(payload: Mapping[str, Any] | list[Any]) -> list[Mapping[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, Mapping)]
    results = payload.get("results", [])
    return [item for item in results if isinstance(item, Mapping)] if isinstance(results, list) else []


def _optional_id(value: Any) -> str | None:
    if isinstance(value, Mapping):
        value = value.get("id")
    return str(value) if value else None


def _looks_like_uuid(value: str) -> bool:
    parts = value.split("-")
    return len(parts) == 5 and all(parts)


def _response_detail(response: HTTPError) -> str:
    try:
        raw = response.read()
        if raw:
            payload = json.loads(raw.decode("utf-8"))
            if isinstance(payload, Mapping):
                return str(payload.get("detail") or payload.get("message") or payload)
            return str(payload)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        pass
    return response.reason or "Plane request failed"
