"""forgestack board — attach AGTX UI."""

import shutil
import subprocess

from rich.console import Console

from ..paths import git_root


def cli() -> None:
    console = Console()
    root = git_root(__import__("pathlib").Path.cwd())

    if not shutil.which("agtx"):
        console.print("[yellow]AGTX not installed.[/yellow]")
        console.print("Install AGTX first: see upstream docs.")
        return

    if root is None:
        console.print("[red]Run from a git repository.[/red]")
        return

    try:
        subprocess.run(["agtx", "project", "-p", str(root)], check=False)
    except FileNotFoundError:
        console.print("[red]AGTX command failed.[/red]")
