"""forgestack status — compact adapter registry view."""

from rich.console import Console
from rich.table import Table

from ..adapters.registry import registry


def cli() -> None:
    console = Console()
    adapters = registry()

    table = Table(title="ForgeStack Status", show_header=True)
    table.add_column("Adapter", style="cyan")
    table.add_column("Installed", justify="center")
    table.add_column("Version")

    for adapter in adapters:
        detect = adapter.detect()
        installed = "✔" if detect.installed else "○"
        version = detect.version or "—"
        table.add_row(adapter.display_name, installed, version)

    console.print(table)
