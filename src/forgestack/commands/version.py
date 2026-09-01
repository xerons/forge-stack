"""forgestack version."""

from importlib.metadata import version as _meta_version


def cli() -> None:
    from rich.console import Console

    cfg = _meta_version("forgestack")
    Console().print(f"forgestack {cfg}")
