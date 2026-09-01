"""forgestack manager — launch Manager agent via herdr if present, else fallback."""

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

    if shutil.which("herdr"):
        console.print("Attaching Herdr workspace (Manager/AGTX/Shell) …")
        subprocess.run(["herdr"], cwd=root)
    else:
        console.print("Herdr missing; start AGTX manager loop manually with your Manager-ready prompt.")
