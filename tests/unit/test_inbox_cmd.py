from types import SimpleNamespace

from forgestack.commands import inbox_cmd


def _setup(monkeypatch, tmp_path):
    monkeypatch.setattr(inbox_cmd, "git_root", lambda _: tmp_path)
    monkeypatch.setattr(inbox_cmd.shutil, "which", lambda _: "/bin/agtx")


def test_failed_query_is_not_reported_clean(tmp_path, monkeypatch, capsys):
    _setup(monkeypatch, tmp_path)
    monkeypatch.setattr(
        inbox_cmd.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=2, stdout="", stderr="unsupported"),
    )
    inbox_cmd.cli()
    output = capsys.readouterr().out
    assert "query failed" in output
    assert "Inbox clean" not in output


def test_empty_success_reports_clean(tmp_path, monkeypatch, capsys):
    _setup(monkeypatch, tmp_path)
    monkeypatch.setattr(
        inbox_cmd.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="", stderr=""),
    )
    inbox_cmd.cli()
    assert "Inbox clean" in capsys.readouterr().out


def test_populated_success_reports_decisions(tmp_path, monkeypatch, capsys):
    _setup(monkeypatch, tmp_path)
    monkeypatch.setattr(
        inbox_cmd.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="task-1 needs review", stderr=""),
    )
    inbox_cmd.cli()
    output = capsys.readouterr().out
    assert "Needs you" in output
    assert "task-1 needs review" in output


def test_failed_query_prints_external_error_as_text(tmp_path, monkeypatch, capsys):
    _setup(monkeypatch, tmp_path)
    monkeypatch.setattr(
        inbox_cmd.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=2,
            stdout="",
            stderr="[link=https://example.invalid]external detail[/link]",
        ),
    )
    inbox_cmd.cli()
    output = capsys.readouterr().out
    assert "[link=https://example.invalid]external detail[/link]" in output
