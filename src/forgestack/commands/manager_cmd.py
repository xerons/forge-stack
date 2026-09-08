"""forgestack manager — launch a persistent, configured Manager session."""

import shutil
import subprocess
from pathlib import Path

from rich.console import Console
from rich.prompt import Confirm

from ..adapters.registry import registry
from ..assets import asset_root
from ..config import load_config
from ..paths import git_root


def cli() -> int:
    console = Console()
    root = git_root(Path.cwd())

    if root is None:
        console.print("[red]Run from a git repository.[/red]")
        return 1

    adapters = registry()
    installed = {a.name: a.detect().installed for a in adapters}
    cfg = load_config(root)
    global_cfg = load_config(None)
    agent = cfg.manager_agent or global_cfg.manager_agent or "codex"
    global_agent = global_cfg.manager_agent or "codex"
    if cfg.manager_agent and cfg.manager_agent != global_agent:
        console.print(
            f"Project config selects Manager agent '{cfg.manager_agent}' "
            f"instead of global '{global_agent}'.",
            markup=False,
        )
        if not Confirm.ask("Launch the project-selected Manager agent?", default=False):
            console.print("Manager launch cancelled.")
            return 1
    instructions = _manager_instructions(root)

    if not installed.get("agtx"):
        console.print("[yellow]AGTX not detected — limited functionality.[/yellow]")

    command = _manager_command(agent, root, instructions)
    if command is None:
        console.print(f"Unsupported Manager agent '{agent}'.", style="red", markup=False)
        console.print(
            'Configure [manager] agent = "codex" or another supported interactive CLI.',
            markup=False,
        )
        return 1

    console.print(f"Launching persistent Manager with {agent} in {root}...", markup=False)
    try:
        result = subprocess.run(command, cwd=root, check=False)
    except (FileNotFoundError, OSError) as exc:
        console.print(f"Manager launch failed: {exc}", style="red", markup=False)
        return 1
    if result.returncode != 0:
        console.print(f"[red]Manager exited with status {result.returncode}.[/red]")
        return result.returncode or 1
    return 0


def _manager_command(agent: str, root: Path, instructions: str) -> list[str] | None:
    """Return the verified interactive launcher for a configured agent."""
    if not shutil.which(agent):
        return None
    if agent == "codex":
        return ["codex", "-C", str(root), instructions]
    if agent == "gemini":
        return ["gemini", "--prompt-interactive", instructions]
    if agent == "opencode":
        return ["opencode", str(root), "--prompt", instructions]
    if agent == "herdr":
        return ["herdr", "--session", "forgestack-manager"]
    return None


def _manager_instructions(root: Path) -> str:
    """Load the product Manager contract without replacing Codex's AGENTS chain."""
    skill = asset_root() / "skills" / "forgestack" / "manager" / "SKILL.md"
    if skill.is_file():
        body = skill.read_text()
    else:
        body = "Coordinate the project as Manager: refine requirements, route AGTX work, and do not implement production code."
    return (
        "You are the ForgeStack Manager for the Git project at "
        f"{root}.\n\n{body}\n\n"
        "Start by inspecting the project and current AGTX task state. Keep the Product Owner "
        "in control of product decisions, and report the next concrete action."
    )
