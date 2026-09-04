"""forgestack setup — detect deps, offer install plan (y/N-only), configure."""

from pathlib import Path

from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table

from .. import paths
from ..adapters.registry import registry
from ..assets import asset_root, plugin_template, skill_suite_files
from ..managed import Status, check, write_managed


def _home() -> Path:  # ponytail: indirection so tests can monkeypatch HOME
    return Path.home()


def _user_agents_dir() -> Path:  # ponytail: indirection so tests can monkeypatch
    return _home() / ".agents"


def cli(dry_run: bool = False, scope: str = "global") -> None:
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

    _install_assets(scope, console)

    if Confirm.ask("Design your workflow phases now? (forgestack phases)", default=False):
        from .phases_cmd import scaffold

        scaffold()


def _install_assets(scope: str, console: Console) -> None:
    """Install/update ForgeStack skills + AGTX plugin into the scope's roots."""
    if not Confirm.ask("Install/update ForgeStack skills + AGTX plugin?", default=True):
        return

    if scope == "project":
        root = paths.git_root(Path.cwd())
        if root is None:
            console.print("[red]Not inside a git repo — skipping project-scope install.[/red]")
            return
        skill_root = root / ".agents"
        plugin_target = root / ".agtx/plugins/forgestack/plugin.toml"
        plugin_manifest_root = root
    else:
        skill_root = _user_agents_dir()
        plugin_target = paths.config_dir() / "agtx/plugins/forgestack/plugin.toml"
        plugin_manifest_root = paths.config_dir()

    written = skipped = 0
    base = asset_root() / "skills"
    for f in skill_suite_files():
        target = skill_root / "skills" / f.relative_to(base)
        result = write_managed(target, skill_root, f.read_text(), source=str(f.relative_to(asset_root())))
        written, skipped = _tally(result, target, skill_root, console, written, skipped)

    result = write_managed(
        plugin_target,
        plugin_manifest_root,
        plugin_template().read_text(),
        source="agtx/plugins/forgestack/plugin.toml",
    )
    written, skipped = _tally(result, plugin_target, plugin_manifest_root, console, written, skipped)

    console.print(f"Assets: {written} written, {skipped} skipped")


def _tally(result: str, target: Path, root: Path, console: Console, written: int, skipped: int) -> tuple[int, int]:
    if result == "written":
        return written + 1, skipped
    reason = "user-modified" if check(target, root) is Status.MODIFIED else "foreign"
    console.print(f"[yellow]skipped ({reason}): {target}[/yellow]")
    return written, skipped + 1
