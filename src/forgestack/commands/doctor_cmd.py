"""forgestack doctor — validate without mutating."""

from rich.console import Console
from rich.table import Table

from ..adapters.registry import registry


def cli() -> int:
    console = Console()
    failures = 0
    table = Table("Check", "Status", "Detail")
    for a in registry():
        for c in a.validate():
            ok = c.ok
            table.add_row(c.name, "[green]ok[/green]" if ok else "[red]fail[/red]", str(c.detail))
            if not ok and getattr(a, "required", False):
                failures += 1
    console.print(table)
    console.print("Doctor: " + ("clean" if failures == 0 else f"{failures} required failure(s)"))
    return 0 if failures == 0 else 1
