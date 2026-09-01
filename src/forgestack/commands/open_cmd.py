"""forgestack open — create/attach standard Herdr workspace."""

from rich.console import Console


def cli() -> None:
    console = Console()
    console.print("Workspace layout: Manager / AGTX / Shell ( Herdr attach expected ).")
