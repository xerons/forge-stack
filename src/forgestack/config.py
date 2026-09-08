"""Unified ForgeStack configuration.

Layered TOML: global config at ``~/.config/forgestack/config.toml`` plus an
optional project config at ``./.forgestack.toml``. Project values win over
global in a deep merge. Reads use stdlib ``tomllib``; writes use a minimal
internal emitter for the owned keys ForgeStack manages.
"""

from __future__ import annotations

import json
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from . import paths
from .workflow.model import PhaseDef


@dataclass
class Config:
    profile: str = "default"
    manager_agent: str | None = None
    workflow_engine: str = "agtx"
    agents: dict[str, str] = field(default_factory=dict)
    integrations: dict[str, str | bool] = field(default_factory=dict)
    runtime_workspace: str | None = None
    values: dict = field(default_factory=dict)
    workflow_research: bool = True
    workflow_cyclic: bool = False
    phases: list[PhaseDef] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> Config:
        mgr = data.get("manager", {})
        wf = data.get("workflow", {})
        return cls(
            profile=data.get("profile", "default"),
            manager_agent=mgr.get("agent"),
            workflow_engine=wf.get("engine", "agtx"),
            agents=data.get("agents", {}),
            integrations=data.get("integrations", {}),
            runtime_workspace=data.get("runtime", {}).get("workspace"),
            workflow_research=bool(wf.get("research", True)),
            workflow_cyclic=bool(wf.get("cyclic", False)),
            phases=_parse_phases(wf.get("phases")),
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
    global_cfg = _read_toml(paths.global_config_path(env))
    project_cfg = {}
    if project_root is not None:
        project_cfg = _read_toml(paths.project_config_path(project_root))
    merged = _deep_merge(global_cfg, project_cfg)
    return Config.from_dict(merged)


def render_toml(config: Config) -> str:
    """Minimal emitter for the owned keys ForgeStack writes."""
    lines = [f'profile = "{config.profile}"', ""]
    if config.manager_agent:
        lines += ["[manager]", f'agent = "{config.manager_agent}"', ""]
    lines += ["[workflow]", _fmt_kv("engine", config.workflow_engine)]
    lines += [
        f"research = {str(config.workflow_research).lower()}",
        f"cyclic = {str(config.workflow_cyclic).lower()}",
        "",
    ]
    for p in config.phases:
        lines.append("[[workflow.phases]]")
        lines.append(_fmt_kv("key", p.key))
        if p.label:
            lines.append(_fmt_kv("label", p.label))
        if p.purpose:
            lines.append(_fmt_kv("purpose", p.purpose))
        if p.agent:
            lines.append(_fmt_kv("agent", p.agent))
        if p.skills:
            lines.append(_fmt_kv("skills", p.skills))
        if p.team:
            lines.append(_fmt_kv("team", p.team))
        if p.artifact:
            lines.append(_fmt_kv("artifact", p.artifact))
        if p.prompt:
            lines.append(_fmt_kv("prompt", p.prompt))
        lines.append("")
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
    rendered = "\n".join(lines).rstrip() + "\n"
    _validate_toml(rendered)
    return rendered


def _fmt_kv(key: str, val) -> str:
    if isinstance(val, bool):
        return f"{key} = {'true' if val else 'false'}"
    if isinstance(val, list):
        items = ", ".join(_toml_string(str(v)) for v in val)
        return f"{key} = [{items}]"
    return f"{key} = {_toml_string(str(val))}"


def _toml_string(value: str) -> str:
    """Encode a TOML basic string without losing escapes or control characters."""
    return json.dumps(value, ensure_ascii=False)


def _validate_toml(text: str) -> None:
    """Fail before a caller writes malformed generated configuration."""
    tomllib.loads(text)


def _parse_phases(raw: object) -> list[PhaseDef]:
    if not isinstance(raw, list):
        return []
    out: list[PhaseDef] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        key = str(item.get("key") or "")
        if not key:
            continue
        out.append(
            PhaseDef(
                key=key,
                label=str(item.get("label") or ""),
                purpose=str(item.get("purpose") or ""),
                agent=str(item.get("agent") or ""),
                skills=[str(s) for s in item.get("skills", [])],
                team=[str(t) for t in item.get("team", [])],
                artifact=str(item["artifact"]) if item.get("artifact") else None,
                prompt=str(item.get("prompt") or ""),
            )
        )
    return out
