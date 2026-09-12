"""Manual tracker-backed orchestration gate."""

from __future__ import annotations

from html import escape
from pathlib import Path

from rich.console import Console

from ..config import load_config
from ..paths import git_root
from ..tracker.errors import TrackerError
from ..tracker.factory import build_tracker


def cli(work_item: str, children: tuple[str, ...] = (), start: bool = False) -> int:
    """Preflight or start one explicitly targeted Plane work item.

    Child creation is intentionally explicit for the first slice. A future
    Manager/Orchestrator agent can produce these names from an approved plan,
    but the CLI must not invent a decomposition silently.
    """
    console = Console()
    root = git_root(Path.cwd())
    if root is None:
        console.print("Run from a git repository.", style="red")
        return 1

    try:
        tracker = build_tracker(load_config(root).tracker)
        target = tracker.get_work_item(work_item)
        if target.state_name != "Ready":
            console.print(
                f"{target.identifier or work_item} is {target.state_name or 'in an unknown state'}; "
                "human approval is required in Ready before orchestration.",
                style="yellow",
            )
            return 2

        states = {state.name.casefold(): state for state in tracker.list_states()}
        ready = states.get("ready")
        in_progress = states.get("in progress")
        if ready is None or in_progress is None:
            console.print("Plane must have Ready and In Progress states.", style="red")
            return 1

        console.print(f"Target: {target.identifier or target.id} — {target.name}")
        if children:
            console.print("Proposed child work items:")
            for name in children:
                console.print(f"  - {name}")
        if not start:
            console.print("Preflight passed. Re-run with --start to apply this orchestration step.")
            return 0

        created = []
        for name in children:
            created.append(
                tracker.create_work_item(
                    name=name,
                    parent_id=target.id,
                    module_id=target.module_id,
                    state_id=ready.id,
                )
            )

        tracker.update_work_item(target.id, state_id=in_progress.id)
        details = "<p><strong>Orchestrator started.</strong></p>"
        if created:
            details += "<p>Created approved child work items:</p><ul>"
            details += "".join(
                f"<li>{escape(item.identifier or item.name)}</li>" for item in created
            )
            details += "</ul>"
        details += "<p>Worker dispatch remains an explicit next step; workers do not update Plane directly.</p>"
        tracker.add_comment(target.id, details)
        console.print(f"Started orchestration for {target.identifier or target.id}.")
        if created:
            console.print(f"Created {len(created)} child work item(s).")
        return 0
    except TrackerError as exc:
        console.print(str(exc), style="red", markup=False)
        return 1
