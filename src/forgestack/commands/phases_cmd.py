"""forgestack phases — design and apply the workflow phase model."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.prompt import Confirm, Prompt

from ..adapters.registry import registry
from ..config import Config, _deep_merge, render_toml
from ..paths import git_root
from ..workflow.model import AGENT_PHASE_KEYS, ALLOWED_PHASE_KEYS, PhaseDef, PhaseModel
from ..workflow.validate import validate

phases_app = typer.Typer(name="phases", help="Design and apply the workflow phase model.")

_DEFAULT_SELECTION = "planning,running,review"

_AGENT_CMDS = {
    "codex": ["codex", "exec"],
    "claude": ["claude", "-p"],
    "opencode": ["opencode", "run"],
}


def _write_scope(
    path: Path,
    phases: list[dict],
    research: bool,
    cyclic: bool,
) -> None:
    existing: dict = {}
    if path.exists():
        import tomllib

        existing = tomllib.loads(path.read_text())
    data = {"workflow": {"engine": "agtx", "research": research, "cyclic": cyclic, "phases": phases}}
    merged = _deep_merge(existing, data)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_toml(Config.from_dict(merged)))


@phases_app.command("scaffold")
def scaffold(scope: str = typer.Option("project", "--scope", help="project or global")) -> None:
    """Collect the deterministic shape: which phases, research/cyclic, agents, skills, team."""
    console = Console()
    root = git_root(Path.cwd()) if scope == "project" else None
    if scope == "project" and root is None:
        console.print("[red]Not a Git repository. Use --scope global.[/red]")
        raise SystemExit(1)

    providers = [a.name for a in registry() if getattr(a, "category", "") == "agents"]
    fallback = (providers or ["codex"])[0]

    choice = Prompt.ask(
        "Phases (comma-separated from research, planning, running, review, preresearch)",
        default=_DEFAULT_SELECTION,
    ).strip().lower()
    keys = [k for k in [s.strip() for s in choice.split(",")] if k]
    for k in keys:
        if k not in ALLOWED_PHASE_KEYS:
            console.print(f"[yellow]Ignoring unknown phase '{k}'[/yellow]")

    research = Confirm.ask("Enable optional research lane?", default=("research" in keys))
    cyclic = Confirm.ask("Cyclic flow (review back to planning)?", default=False)

    phases: list[dict] = []
    for k in keys:
        if k not in AGENT_PHASE_KEYS:
            phases.append({"key": k, "purpose": ""})
            continue
        agent = Prompt.ask(f"Agent for '{k}'", choices=providers or ["codex"], default=fallback)
        skills = Prompt.ask(f"Skill packs for '{k}' (comma-separated, optional)", default="")
        skills = [s.strip() for s in skills.split(",") if s.strip()]
        phase: dict = {"key": k, "agent": agent}
        if skills:
            phase["skills"] = skills
        if k == "planning" and Confirm.ask(
            "Add multidisciplinary team to planning? (extra tokens, opt-in)", default=False
        ):
            team = Prompt.ask("Team roster (comma-separated roles)", default="")
            phase["team"] = [t.strip() for t in team.split(",") if t.strip()]
        phases.append(phase)

    if scope == "project":
        from ..paths import project_config_path

        path = project_config_path(root)
    else:
        from ..paths import global_config_path

        path = global_config_path()
    _write_scope(path, phases, research, cyclic)
    console.print("Scaffold written. Next: [bold]forgestack phases design[/bold] to fill content.")


@phases_app.command("design")
def design(scope: str = typer.Option("project", "--scope", help="project or global")) -> None:
    """Co-design per-phase content with the configured agent."""
    console = Console()
    from ..config import load_config

    root = git_root(Path.cwd()) if scope == "project" else None
    cfg = load_config(root)
    if not cfg.phases:
        console.print("[yellow]No phases in config yet — run 'phases scaffold' first.[/yellow]")
        return
    model = PhaseModel(research=cfg.workflow_research, cyclic=cfg.workflow_cyclic)
    model.phases = cfg.phases

    agent = next((p.agent for p in cfg.phases if p.agent), None) or cfg.manager_agent or "codex"
    cmd = _agent_command(agent)
    if cmd is None or not git_root(Path.cwd()):
        console.print(
            f"[yellow]Agent '{agent}' has no one-shot launcher here. Edit purpose/prompt "
            "directly in your config, or run 'phases apply' to ship default prompts.[/yellow]"
        )
        return

    prompt = _design_prompt(model)
    try:
        import subprocess

        result = subprocess.run(
            cmd + [prompt],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except (FileNotFoundError, TimeoutError) as exc:
        console.print(f"[yellow]Agent run failed ({exc}). Defaults will be applied.[/yellow]")
        return
    merged = _merge_design_toml(model, result.stdout)
    if merged is None:
        console.print("[yellow]No parseable TOML returned — defaults will be applied.[/yellow]")
        return
    model = merged
    _write_scope(_scope_path(scope, root), _phases_to_dicts(model.phases), model.research, model.cyclic)
    console.print("Design merged into config. Run [bold]phases apply[/bold] to regenerate the AGTX plugin.")


@phases_app.command("apply")
def apply(scope: str = typer.Option("project", "--scope", help="project or global")) -> None:
    """Render plugin.toml + [agents] wiring, backup, diff, y/N write."""
    console = Console()
    root = git_root(Path.cwd()) if scope == "project" else None
    from ..config import load_config

    cfg = load_config(root)
    model = PhaseModel(research=cfg.workflow_research, cyclic=cfg.workflow_cyclic)
    model.phases = cfg.phases
    if not model.phases:
        model = PhaseModel.default()
    issues = [r for r in validate(model, registry()) if not r.ok]
    if issues:
        for i in issues:
            console.print(f"[red]{i.name}: {i.detail}[/red]")
        console.print("[red]Fix the model before applying.[/red]")
        raise SystemExit(1)

    from ..workflow.renderer import render_agents_config, render_plugin_toml

    plugin_path = _plugin_path(scope, root)
    backup = _backup(plugin_path)
    if backup:
        console.print(f"Backed up to {backup}")
    rendered = render_plugin_toml(model)
    plugin_path.parent.mkdir(parents=True, exist_ok=True)
    _write_with_diff(console, plugin_path, rendered)
    agents = render_agents_config(model)
    if agents:
        console.print("AGTX [agents] wiring to add to your agtx config.toml:")
        console.print("```toml\n[agents]\n" + "".join(f'{k} = "{v}"\n' for k, v in agents.items()) + "```")
    console.print("[green]Next: 'forgestack status' to check detection, then run AGTX.[/green]")


def _design_prompt(model: PhaseModel) -> str:
    lines = [
        (
            "You are designing the ForgeStack workflow phase model. For EACH phase below, "
            "write (a) a one-paragraph 'purpose' and (b) a complete agent 'prompt' that starts "
            "with 'Task:\\n{task}' and guides that phase. Return ONLY a TOML fenced block:"
        ),
        "```toml",
        "[[workflow.phases]]",
        'key = "<key>"',
        'purpose = "..."',
        'prompt = """..."""',
        "```",
        "",
    ]
    for p in model.phases:
        lines.append(f"## phase key={p.key}" + (f" agent={p.agent}" if p.agent else ""))
        if p.team:
            lines.append("team (sprint-planning): " + ", ".join(p.team))
            lines.append("include role passes and a requirements × roles coverage matrix.")
        if p.skills:
            lines.append("available skills: " + ", ".join(p.skills))
        lines.append(f"current purpose: {p.purpose or '(none)'}")
    return "\n".join(lines)


def _merge_design_toml(model: PhaseModel, stdout: str) -> PhaseModel | None:
    block = _extract_toml(stdout)
    if block is None:
        return None
    import tomllib

    try:
        data = tomllib.loads(block)
    except (ValueError, KeyError):
        return None
    phases = data.get("workflow", {}).get("phases")
    if not isinstance(phases, list):
        return None
    by_key = {p.key: p for p in model.phases}
    for item in phases:
        if not isinstance(item, dict):
            continue
        if item.get("key") in by_key:
            existing = by_key[item["key"]]
            if item.get("purpose") is not None:
                existing.purpose = str(item["purpose"])
            if item.get("prompt") is not None:
                existing.prompt = str(item["prompt"])
    return model


def _extract_toml(text: str) -> str | None:
    start = text.find("```toml")
    if start < 0:
        start = text.find("```\n[[workflow.phases]]")
    if start < 0:
        return None
    body = text[start:]
    body = body.split("```", 2)
    if len(body) < 2:
        return None
    return body[1] if body[1] else None


def _phases_to_dicts(phases: list[PhaseDef]) -> list[dict]:
    return [
        {
            "key": p.key,
            **({"label": p.label} if p.label else {}),
            **({"purpose": p.purpose} if p.purpose else {}),
            **({"agent": p.agent} if p.agent else {}),
            **({"skills": p.skills} if p.skills else {}),
            **({"team": p.team} if p.team else {}),
            **({"artifact": p.artifact} if p.artifact else {}),
            **({"prompt": p.prompt} if p.prompt else {}),
        }
        for p in phases
    ]


def _agent_command(agent: str) -> list[str] | None:
    return _AGENT_CMDS.get(agent)


def _scope_path(scope: str, root: Path | None) -> Path:
    from ..paths import global_config_path, project_config_path

    if scope == "project" and root is not None:
        return project_config_path(root)
    return global_config_path()


def _plugin_path(scope: str, root: Path | None) -> Path:
    if scope == "project" and root is not None:
        base = root / ".agtx" / "plugins" / "forgestack"
    else:
        from ..paths import config_dir

        base = config_dir() / "agtx" / "plugins" / "forgestack"
    return base / "plugin.toml"


def _backup(path: Path) -> Path | None:
    if not path.exists():
        return None
    backup = path.with_suffix(path.suffix + ".bak")
    backup.write_text(path.read_text())
    return backup


def _write_with_diff(console: Console, path: Path, new: str) -> None:
    import difflib

    old = path.read_text() if path.exists() else ""
    if old == new:
        console.print("[green]plugin.toml unchanged.[/green]")
        return
    for line in difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm=""):
        console.print(line)
    if Confirm.ask("Write plugin.toml?"):
        path.write_text(new)
        console.print(f"Wrote {path}")
    else:
        console.print("Skipped.")
