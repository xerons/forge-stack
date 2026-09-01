"""forgestack manager — launch Manager agent via herdr if present, else fallback."""

import subprocess
from pathlib import Path

from rich.console import Console

from ..adapters.registry import registry
from ..paths import git_root


def cli() -> None:
    console = Console()
    root = git_root(Path.cwd())

    if root is None:
        console.print("[red]Run from a git repository.[/red]")
        return

    # Check adapters
    adapters = registry()
    installed = {a.name: a.detect().installed for a in adapters}

    if not installed.get("agtx"):
        console.print("[yellow]AGTX not detected — limited functionality.[/yellow]")

    if not installed.get("herdr"):
        console.print("[yellow]Herdr not detected — workspace unavailable.[/yellow]")
        console.print("Start AGTX manager loop manually with your Manager-ready prompt.")
        return

    # Launch Herdr workspace
    console.print("Attaching Herdr workspace (Manager / AGTX / Shell)...")
    try:
        subprocess.run(["herdr"], cwd=root, check=False)
    except FileNotFoundError:
        console.print("[red]Herdr command failed.[/red]")
