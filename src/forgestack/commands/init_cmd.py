"""forgestack init — project bootstrap."""

from rich.console import Console
from rich.table import Table

from ..adapters.bmad import BmadAdapter
from ..config import load_config
from ..paths import git_root


def cli() -> None:
    console = Console()
    root = git_root(__import__("pathlib").Path.cwd())
    if root is None:
        console.print("[red]Not a Git repository[/red]")
        return

    cfg = load_config(root)
    checks = [("Git repository", root is not None)]
    bmad = BmadAdapter(root).detect()
    checks.append(("Global profile loaded", bool(cfg.profile)))
    checks.append(("Agent routing", bool(cfg.agents)))
    checks.append(("BMAD detected", bool(bmad.installed)))
    checks.append(("Worktree compat", (root / ".git").exists()))

    console.print(_render(checks))
    console.print("Project ready.")


def _render(checks: list[tuple[str, bool]]) -> Table:
    table = Table("Check", "Result")
    for name, ok in checks:
        table.add_row(name, "✔" if ok else "○")
    return table
