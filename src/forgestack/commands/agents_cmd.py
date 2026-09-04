"""forgestack agents — dynamic provider-agnostic routing config."""

from rich.console import Console
from rich.prompt import Prompt

from .. import paths
from ..adapters.registry import registry
from ..config import Config, load_config, render_toml


def cli() -> None:
    console = Console()
    cfg = load_config(paths.git_root(__import__("pathlib").Path.cwd()))
    providers = [a.name for a in registry() if getattr(a, "category", "") == "agents"]

    roles = ["research", "planning", "running", "review"]
    fallback = (providers or ["codex"])[0]
    new_agents: dict[str, str] = {}

    console.print(f"Detected agent CLIs: {', '.join(providers) or 'none'}")
    for role in roles:
        preferred = cfg.agents.get(role) or fallback
        choice = Prompt.ask(
            f"[agents]{role}",
            choices=providers or ["codex"],
            default=preferred if preferred in providers else fallback,
        )
        new_agents[role] = choice

    # Mutate the loaded cfg so phases/workflow flags/values survive the write.
    cfg.agents = new_agents
    _write_config_safe(cfg, console)


def _write_config_safe(cfg: Config, console: Console) -> None:
    from ..managed import write_managed

    path = paths.config_dir() / "config.toml"
    content = render_toml(cfg)
    result = write_managed(path, paths.config_dir(), content, source="config.toml")
    if result == "skipped":
        console.print("[yellow]Skipped config.toml — user-modified or foreign.[/yellow]")
    else:
        console.print(f"Written unified config at {path}")
