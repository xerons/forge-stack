"""Render a PhaseModel into AGTX plugin.toml and [agents] config."""

from __future__ import annotations

import json
import tomllib

from .model import AGENT_PHASE_KEYS, DEFAULT_PROMPTS, PhaseModel


def render_plugin_toml(
    model: PhaseModel,
    plugin_name: str = "forgestack",
    plugin_description: str = "Research → planning → implementation → independent review",
) -> str:
    lines = [
        f"name = {_toml_string(plugin_name)}",
        f"description = {_toml_string(plugin_description)}",
        f"cyclic = {str(model.cyclic).lower()}",
    ]
    prompt_blocks: list[str] = []
    command_blocks: list[str] = []
    artifact_lines: list[str] = []
    for p in model.phases:
        if p.key == "research" and not model.research:
            continue
        if p.key == "preresearch":
            command_blocks.append("[commands]")
            command_blocks.append(f"preresearch = {_toml_string(_phase_text(p))}")
            continue
        prompt_blocks.append(f"{p.key} = {_toml_string(_phase_text(p))}")
        if p.artifact:
            artifact_lines.append(
                f"{p.key} = {_toml_string(f'docs/{plugin_name}/{p.artifact}')}"
            )
    if prompt_blocks:
        lines.append("")
        lines.append("[prompts]")
        lines += prompt_blocks
    if command_blocks:
        lines.append("")
        lines += command_blocks
    if artifact_lines:
        lines.append("")
        lines.append("[artifacts]")
        lines += artifact_lines
    rendered = "\n".join(lines) + "\n"
    tomllib.loads(rendered)
    return rendered


def render_agents_config(model: PhaseModel) -> dict[str, str]:
    return {p.key: p.agent for p in model.phases if p.key in AGENT_PHASE_KEYS and p.agent}


def _toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _phase_text(p) -> str:
    body = p.prompt.strip() if p.prompt else DEFAULT_PROMPTS.get(p.key, "Task:\n{task}")
    parts = [body]
    if p.skills:
        packs = ", ".join(p.skills)
        parts.append(
            "Use relevant available skill packs within user scope and permissions; never vendor: "
            + packs
            + "."
        )
    if p.team and p.key == "planning":
        roles = ", ".join(p.team)
        parts.append(
            "Multidisciplinary sprint-planning (enabled): simulate this team working the "
            f"story together — {roles}. Run one explicit role pass per member (deliverables, "
            "owned requirements, risks, commonly-overlooked items). Delegate bounded independent "
            "passes only when supported and authorized by the active user/harness policy; "
            "the roster does not waive spawn approval. Otherwise label these as one agent's "
            "role perspectives, not independent review. Produce a requirements × roles "
            "coverage matrix in the planning artifact and flag any requirement uncovered "
            "by the team as a gap before decomposition. Still do not implement production code."
        )
    return "\n".join(parts)
