from pathlib import Path
from types import SimpleNamespace

from forgestack.commands import orchestrate_cmd
from forgestack.tracker.protocol import TrackerState, TrackerWorkItem


def make_item(state_name: str) -> TrackerWorkItem:
    return TrackerWorkItem(
        id="parent-id",
        identifier="FS-4",
        name="Evaluate Plane",
        state_id=f"{state_name.lower()}-id",
        state_name=state_name,
        state_group="unstarted" if state_name in {"Todo", "Ready"} else "started",
        project_id="project-id",
        module_id="module-id",
    )


class FakeTracker:
    def __init__(self, state_name: str = "Ready") -> None:
        self.target = make_item(state_name)
        self.created: list[dict] = []
        self.updated: list[dict] = []
        self.comments: list[tuple[str, str]] = []

    def get_work_item(self, identifier: str) -> TrackerWorkItem:
        assert identifier == "FS-4"
        return self.target

    def list_states(self) -> list[TrackerState]:
        return [
            TrackerState("ready-id", "Ready", "unstarted"),
            TrackerState("progress-id", "In Progress", "started"),
        ]

    def create_work_item(self, **kwargs):
        self.created.append(kwargs)
        return make_item("Ready")

    def update_work_item(self, work_item_id: str, **kwargs):
        self.updated.append({"id": work_item_id, **kwargs})
        return make_item("In Progress")

    def add_comment(self, work_item_id: str, comment_html: str) -> None:
        self.comments.append((work_item_id, comment_html))


def setup(monkeypatch, tmp_path: Path, tracker: FakeTracker) -> None:
    monkeypatch.setattr(orchestrate_cmd, "git_root", lambda _: tmp_path)
    monkeypatch.setattr(
        orchestrate_cmd,
        "load_config",
        lambda _: SimpleNamespace(tracker=SimpleNamespace()),
    )
    monkeypatch.setattr(orchestrate_cmd, "build_tracker", lambda _: tracker)


def test_orchestrator_preflight_requires_ready(monkeypatch, tmp_path, capsys) -> None:
    tracker = FakeTracker("Todo")
    setup(monkeypatch, tmp_path, tracker)

    assert orchestrate_cmd.cli("FS-4") == 2
    assert "human approval" in capsys.readouterr().out
    assert tracker.created == []


def test_orchestrator_starts_and_creates_explicit_children(monkeypatch, tmp_path) -> None:
    tracker = FakeTracker()
    setup(monkeypatch, tmp_path, tracker)

    assert orchestrate_cmd.cli("FS-4", ("Implement provider", "Add tests"), start=True) == 0
    assert [item["name"] for item in tracker.created] == ["Implement provider", "Add tests"]
    assert all(item["parent_id"] == "parent-id" for item in tracker.created)
    assert all(item["module_id"] == "module-id" for item in tracker.created)
    assert tracker.updated == [{"id": "parent-id", "state_id": "progress-id"}]
    assert tracker.comments and "Orchestrator started" in tracker.comments[0][1]
