"""Managed-file ownership manifest.

ForgeStack records every file it installs in ``<root>/.forgestack-managed.json``.
A file we wrote and the user has not edited is SAFE to overwrite; a file the
user edited (MODIFIED) or that exists but is not ours (FOREIGN) is never
overwritten. Empty untracked files count as ABSENT.
"""

import hashlib
import json
import os
import tempfile
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path

MANIFEST_NAME = ".forgestack-managed.json"


class Status(Enum):
    ABSENT = "absent"
    SAFE = "safe"
    MODIFIED = "modified"
    FOREIGN = "foreign"


def _manifest_path(root: Path) -> Path:
    return root / MANIFEST_NAME


def _load(root: Path) -> dict:
    """Return the manifest dict; a missing or corrupt manifest reads as empty."""
    try:
        data = json.loads(_manifest_path(root).read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("files"), dict):
            return data
    except (OSError, json.JSONDecodeError):
        pass
    return {"version": 1, "files": {}}


def _save(root: Path, data: dict) -> None:
    """Atomically replace the manifest: temp file in the same dir, then os.replace."""
    manifest = _manifest_path(root)
    fd, tmp = tempfile.mkstemp(dir=root, prefix=MANIFEST_NAME + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
            fh.write("\n")
        os.replace(tmp, manifest)
    finally:
        if os.path.exists(tmp):  # ponytail: cleanup only on failure; replace already moved it
            os.unlink(tmp)


def _key(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def check(path: Path, root: Path) -> Status:
    if not path.exists():
        return Status.ABSENT
    entry = _load(root)["files"].get(_key(path, root))
    if entry is None:
        return Status.FOREIGN if path.stat().st_size > 0 else Status.ABSENT
    current = hashlib.sha256(path.read_bytes()).hexdigest()
    return Status.SAFE if current == entry.get("sha256") else Status.MODIFIED


def write_managed(path: Path, root: Path, content: str, source: str) -> str:
    """Write content if we own the file or it does not exist; else leave it untouched."""
    if check(path, root) in (Status.MODIFIED, Status.FOREIGN):
        return "skipped"
    encoded = content.encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    manifest = _load(root)
    manifest["files"][_key(path, root)] = {
        "sha256": hashlib.sha256(encoded).hexdigest(),
        "installed_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": source,
    }
    _save(root, manifest)
    return "written"
