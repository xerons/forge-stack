from forgestack.tracker.config import TrackerConfig
from forgestack.tracker.doctor import checks


def test_tracker_doctor_reports_unconfigured_as_optional() -> None:
    result = checks(TrackerConfig())
    assert result[0].ok
    assert result[0].detail == "not configured"


def test_tracker_doctor_checks_plane_configuration_and_key(monkeypatch) -> None:
    config = TrackerConfig(
        provider="plane",
        workspace_slug="workspace",
        project_id="project",
        project_identifier="FS",
    )
    monkeypatch.delenv("PLANE_API_KEY", raising=False)

    results = checks(config)

    assert results[0].ok
    assert results[1].ok
    assert not results[2].ok
