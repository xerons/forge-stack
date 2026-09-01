"""forgestack agents — dynamic provider-agnostic routing config."""

from rich.console import Console
from rich.prompt import Prompt

from ..adapters.registry import registry
from ..config import Config, load_config, render_toml
from ..paths import git_root


def cli() -> None:
    console = Console()
    cfg = load_config(git_root(__import__("pathlib").Path.cwd()))
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

    merged = Config(
        profile=cfg.profile,
        manager_agent=cfg.manager_agent,
        workflow_engine=cfg.workflow_engine,
        agents=new_agents,
        integrations=cfg.integrations,
        runtime_workspace=cfg.runtime_workspace,
    )
    _write_config_safe(merged, console)


def _write_config_safe(cfg: Config, console: Console) -> None:
    from ..paths import global_config_path

    path = global_config_path()
    if path.exists():
        backup = path.with_suffix(".toml.bak")
        backup.write_text(path.read_text())
        console.print(f"Backed up current global config to {backup}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_toml(cfg))
    console.print(f"Written unified config at {path}")
