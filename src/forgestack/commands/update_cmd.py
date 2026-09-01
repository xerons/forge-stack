"""forgestack update — ForgeStack self-update, then report external deps update hints."""

from rich.console import Console


def cli() -> None:
    console = Console()
    console.print(
        "update: self-update via your package manager; then run upstream update hints per adapter."
    )
