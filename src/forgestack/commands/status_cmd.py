"""forgestack status — compact engineering view from AGTX when available."""

from rich.console import Console


def cli() -> None:
    console = Console()
    console.print("status: attach AGTX and render lanes when agent CLI supports. MVP stub.")
