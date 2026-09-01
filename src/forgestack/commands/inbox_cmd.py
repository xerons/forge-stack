"""forgestack inbox — Human Inbox view."""

from rich.console import Console


def cli() -> None:
    console = Console()
    console.print("inbox: read AGTX-facing attention items in MVP; no raw-terminal peek requirement.")
