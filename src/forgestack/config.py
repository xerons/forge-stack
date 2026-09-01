"""Unified ForgeStack configuration.

Layered TOML: global config at ``~/.config/forgestack/config.toml`` plus an
optional project config at ``./.forgestack.toml``. Project values win over
global in a deep merge. Reads use stdlib ``tomllib``; writes use a minimal
internal emitter for the owned keys ForgeStack manages.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import tomllib

from .paths import global_config_path, project_config_path


@dataclass
class Config:
    profile: str = "default"
    manager_agent: str | None = None
    workflow_engine: str = "agtx"
    agents: dict[str, str] = field(default_factory=dict)
    integrations: dict[str, str | bool] = field(default_factory=dict)
    runtime_workspace: str | None = None
    values: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        mgr = data.get("manager", {})
        wf = data.get("workflow", {})
        return cls(
            profile=data.get("profile", "default"),
            manager_agent=mgr.get("agent"),
            workflow_engine=wf.get("engine", "agtx"),
            agents=data.get("agents", {}),
            integrations=data.get("integrations", {}),
            runtime_workspace=data.get("runtime", {}).get("workspace"),
            values=data,
        )


def _deep_merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for key, val in override.items():
        if isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], val)
        else:
            out[key] = val
    return out


def _read_toml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("rb") as fh:
        return tomllib.load(fh)


def load_config(project_root: Path | None = None, env: dict | None = None) -> Config:
    global_cfg = _read_toml(global_config_path(env))
    project_cfg = {}
    if project_root is not None:
        project_cfg = _read_toml(project_config_path(project_root))
    merged = _deep_merge(global_cfg, project_cfg)
    return Config.from_dict(merged)


def render_toml(config: Config) -> str:
    """Minimal emitter for the owned keys ForgeStack writes."""
    lines = [f'profile = "{config.profile}"', ""]
    if config.manager_agent:
        lines += ["[manager]", f'agent = "{config.manager_agent}"', ""]
    lines += ["[workflow]", f'engine = "{config.workflow_engine}"', ""]
    if config.agents:
        lines.append("[agents]")
        for key, val in config.agents.items():
            lines.append(_fmt_kv(key, val))
        lines.append("")
    if config.integrations:
        lines.append("[integrations]")
        for key, val in config.integrations.items():
            lines.append(_fmt_kv(key, val))
        lines.append("")
    if config.runtime_workspace:
        lines += ["[runtime]", f'workspace = "{config.runtime_workspace}"', ""]
    return "\n".join(lines).rstrip() + "\n"


def _fmt_kv(key: str, val) -> str:
    if isinstance(val, bool):
        return f"{key} = {'true' if val else 'false'}"
    return f'{key} = "{val}"'
