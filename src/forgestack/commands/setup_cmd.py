"""forgestack setup — detect deps, offer install plan (y/N-only), configure."""

from rich.console import Console
from rich.table import Table

from ..adapters.registry import registry


def cli(dry_run: bool = False) -> None:
    console = Console()
    console.print("[bold]ForgeStack setup[/bold]")

    table = Table("Tool", "Category", "Required", "Status", "Upstream-install hint")
    missing: list[tuple] = []
    for a in registry():
        d = a.detect()
        note = getattr(a, "upstream_hint", getattr(a, "install_hint", ""))
        table.add_row(
            a.name,
            getattr(a, "category", ""),
            "required" if getattr(a, "required", False) else "optional",
            "[green]ok[/green]" if d.installed else "[red]missing[/red]",
            note or "",
        )
        if not d.installed:
            missing.append((a.name, getattr(a, "upstream_hint", getattr(a, "install_hint", "")),
                            getattr(a, "required", False)))

    console.print(table)

    if not missing:
        console.print("All detected or optional-missing without required ones.")
    else:
        console.print("\nMissing tools:")
        for name, hint, req in missing:
            console.print(f" - [{req and 'required' or 'optional'}] {name}: {hint or 'see docs'}")
        console.print(
            "[yellow]Run install via upstream instructions above? [y/N][/yellow]",
            end=" ",
        )
        if not dry_run and input().strip().lower() == "y":
            console.print("(approved) — executing upstream hints manually (automation disabled)")
        else:
            console.print("(skipped) — run `forgestack setup` again after installing.")
