"""Unit tests for adapter registry."""

from forgestack.adapters.registry import registry


def test_registry_returns_sorted_adapter_list() -> None:
    adapters = registry()
    assert isinstance(adapters, list)
    assert len(adapters) > 0
    names = {a.name for a in adapters}
    assert "agtx" in names
    assert "bmad" in names
    assert "matt" in names
    assert "superpowers" in names
    assert "rtk" in names


def test_registry_idempotent() -> None:
    first = registry()
    second = registry()
    assert [a.name for a in first] == [a.name for a in second]
