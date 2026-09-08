"""forgestack inbox — Human Inbox view."""

import shutil
import subprocess

from rich.console import Console

from ..paths import git_root


def cli() -> None:
    console = Console()
    root = git_root(__import__("pathlib").Path.cwd())

    if not shutil.which("agtx"):
        console.print("[yellow]AGTX not installed — inbox unavailable.[/yellow]")
        console.print("Install AGTX first: see upstream docs.")
        return

    if root is None:
        console.print("[red]Run from a git repository.[/red]")
        return

    # Query AGTX for tasks needing attention
    try:
        result = subprocess.run(
            ["agtx", "tasks", "--status", "needs_review"],
            capture_output=True,
            text=True,
            cwd=root,
            timeout=5,
            check=False,
        )
        if result.returncode != 0:
            detail = result.stderr.strip() or f"exit status {result.returncode}"
            console.print(f"AGTX inbox query failed: {detail}", style="red", markup=False)
        elif result.stdout.strip():
            console.print("[bold]Needs you:[/bold]")
            console.print(result.stdout.strip())
        else:
            console.print("[green]Inbox clean — no pending decisions.[/green]")
    except FileNotFoundError:
        console.print("[yellow]AGTX tasks command unavailable.[/yellow]")
    except subprocess.TimeoutExpired:
        console.print("[yellow]AGTX timed out — try again later.[/yellow]")
