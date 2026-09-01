"""forgestack open — create/attach standard Herdr workspace."""

import shutil
import subprocess

from rich.console import Console

from ..paths import git_root


def cli() -> None:
    console = Console()
    root = git_root(__import__("pathlib").Path.cwd())

    if root is None:
        console.print("[red]Run from a git repository.[/red]")
        return

    if not shutil.which("herdr"):
        console.print("[yellow]Herdr not installed — cannot create workspace.[/yellow]")
        console.print("Install Herdr first: see upstream docs.")
        return

    console.print("Attaching Herdr workspace (Manager / AGTX / Shell)...")
    try:
        subprocess.run(["herdr"], cwd=root, check=False)
    except FileNotFoundError:
        console.print("[red]Herdr command failed.[/red]")
