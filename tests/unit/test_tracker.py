import json
from urllib.parse import urlparse

import pytest

from forgestack.tracker.config import TrackerConfig
from forgestack.tracker.errors import TrackerConfigurationError
from forgestack.tracker.factory import build_tracker
from forgestack.tracker.plane import PlaneClient


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode()

    def read(self):
        return self.payload

    def close(self):
        pass


def make_client(responses, calls):
    def opener(request, timeout):
        calls.append((request.method, request.full_url, request.headers, request.data))
        return FakeResponse(responses.pop(0))

    return PlaneClient(
        base_url="https://api.plane.so",
        workspace_slug="my-workspace",
        project_id="project-id",
        project_identifier="FS",
        api_key="plane_api_test",
        opener=opener,
    )


def test_plane_retrieves_work_item_by_identifier_and_expands_state():
    calls = []
    client = make_client(
        [
            {
                "id": "work-id",
                "sequence_id": 4,
                "name": "Evaluate Plane",
                "state": {"id": "ready-id", "name": "Ready", "group": "unstarted"},
                "module": {"id": "module-id"},
                "project": "project-id",
            }
        ],
        calls,
    )

    item = client.get_work_item("FS-4")

    assert item.identifier == "FS-4"
    assert item.state_name == "Ready"
    assert item.module_id == "module-id"
    assert urlparse(calls[0][1]).path.endswith("/work-items/FS-4/")
    assert calls[0][2]["X-api-key"] == "plane_api_test"


def test_plane_updates_state_and_creates_comment():
    calls = []
    client = make_client(
        [
            {"id": "work-id", "sequence_id": 4, "name": "Evaluate Plane", "state": "progress-id"},
            {"results": []},
            {},
        ],
        calls,
    )

    client.update_work_item("work-id", state_id="progress-id")
    client.add_comment("work-id", "started")

    assert calls[0][0] == "PATCH"
    assert json.loads(calls[0][3]) == {"state": "progress-id"}
    assert calls[2][0] == "POST"
    assert json.loads(calls[2][3]) == {"comment_html": "started", "access": "INTERNAL"}


def test_plane_requires_explicit_config_and_api_key(monkeypatch):
    with pytest.raises(TrackerConfigurationError):
        build_tracker(TrackerConfig(provider=""))

    config = TrackerConfig(
        provider="plane",
        workspace_slug="workspace",
        project_id="project",
        project_identifier="FS",
    )
    monkeypatch.delenv("PLANE_API_KEY", raising=False)
    with pytest.raises(TrackerConfigurationError, match="PLANE_API_KEY"):
        build_tracker(config)


def test_plane_uses_project_identifier_for_missing_identifier():
    calls = []
    client = make_client(
        [
            {
                "id": "work-id",
                "sequence_id": 7,
                "name": "Child",
                "state": {"id": "todo-id", "name": "Todo", "group": "unstarted"},
            }
        ],
        calls,
    )

    assert client.get_work_item("FS-7").identifier == "FS-7"
