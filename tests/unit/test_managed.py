"""Tests for forgestack.managed — owned-file tracking and safe-overwrite semantics."""

import hashlib
import json
from pathlib import Path

from forgestack.managed import Status, check, write_managed

MANIFEST = ".forgestack-managed.json"


def read_manifest(root: Path) -> dict:
    return json.loads((root / MANIFEST).read_text(encoding="utf-8"))


def test_absent_file_is_written_and_recorded(tmp_path: Path) -> None:
    target = tmp_path / "skills/forgestack/SKILL.md"
    result = write_managed(target, tmp_path, "# ForgeStack\n", "skills/forgestack/SKILL.md")
    assert result == "written"
    assert target.read_text(encoding="utf-8") == "# ForgeStack\n"
    files = read_manifest(tmp_path)["files"]
    entry = files["skills/forgestack/SKILL.md"]
    assert entry["sha256"] == hashlib.sha256(b"# ForgeStack\n").hexdigest()
    assert entry["source"] == "skills/forgestack/SKILL.md"
    assert entry["installed_at"].endswith("Z")


def test_safe_file_is_rewritten(tmp_path: Path) -> None:
    target = tmp_path / "a.txt"
    write_managed(target, tmp_path, "old", "a.txt")
    assert check(target, tmp_path) is Status.SAFE
    assert write_managed(target, tmp_path, "new", "a.txt") == "written"
    assert target.read_text(encoding="utf-8") == "new"


def test_modified_file_is_skipped(tmp_path: Path) -> None:
    target = tmp_path / "a.txt"
    write_managed(target, tmp_path, "ours", "a.txt")
    target.write_text("user edits", encoding="utf-8")
    assert check(target, tmp_path) is Status.MODIFIED
    assert write_managed(target, tmp_path, "overwrite attempt", "a.txt") == "skipped"
    assert target.read_text(encoding="utf-8") == "user edits"


def test_foreign_file_is_skipped(tmp_path: Path) -> None:
    target = tmp_path / "unrelated.txt"
    target.write_text("not ours\n", encoding="utf-8")
    assert check(target, tmp_path) is Status.FOREIGN
    assert write_managed(target, tmp_path, "ours", "unrelated.txt") == "skipped"
    assert target.read_text(encoding="utf-8") == "not ours\n"


def test_empty_untracked_file_is_written(tmp_path: Path) -> None:
    target = tmp_path / "empty.txt"
    target.touch()
    assert check(target, tmp_path) is Status.ABSENT
    assert write_managed(target, tmp_path, "content", "empty.txt") == "written"


def test_no_temp_files_left_after_save(tmp_path: Path) -> None:
    write_managed(tmp_path / "a.txt", tmp_path, "x", "a.txt")
    write_managed(tmp_path / "b.txt", tmp_path, "y", "b.txt")
    names = {p.name for p in tmp_path.iterdir()}
    assert names == {"a.txt", "b.txt", MANIFEST}


def test_corrupt_manifest_behaves_as_empty(tmp_path: Path) -> None:
    target = tmp_path / "a.txt"
    write_managed(target, tmp_path, "ours", "a.txt")
    (tmp_path / MANIFEST).write_text("{ not json", encoding="utf-8")
    assert check(target, tmp_path) is Status.FOREIGN
    assert write_managed(target, tmp_path, "new ours", "a.txt") == "skipped"
    assert target.read_text(encoding="utf-8") == "ours"
    assert check(tmp_path / "missing.txt", tmp_path) is Status.ABSENT
