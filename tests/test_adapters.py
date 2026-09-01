"""Self-check: adapters + CheckResult constructor ponytail-safe."""

from forgestack.adapters.agtx import AgtxAdapter
from forgestack.adapters.herdr import HerdrAdapter
from forgestack.adapters.protocol import CheckResult
from forgestack.adapters.rtk import RtkAdapter


def test_check_result_str_or_empty() -> None:
    r = CheckResult("name", ok=True)
    assert r.detail == ""
    r2 = CheckResult("name", ok=True, detail="x")
    assert r2.detail == "x"


def test_adapters_validate_no_crash() -> None:
    for cls in (AgtxAdapter, RtkAdapter, HerdrAdapter):
        inst = cls()
        results = inst.validate()
        assert isinstance(results, list)
