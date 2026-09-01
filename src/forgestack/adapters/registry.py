"""Adapter registry — manifest-driven, replaceable per spec."""

from __future__ import annotations

from collections.abc import Iterable

from .agents import make_agent_adapter
from .agtx import AgtxAdapter
from .bmad import BmadAdapter
from .code_server import CodeServerAdapter
from .herdr import HerdrAdapter
from .matt import MattAdapter
from .rtk import RtkAdapter
from .superpowers import SuperpowersAdapter

_AGENT_SPECS = [
    ("codex", "brew install --cask codex"),
    ("claude", "brew install claude"),
    ("opencode", "brew install opencode"),
    ("gemini", "npm install -g @google/gemini-cli"),
    ("agy", "install via official docs"),
]


def registry():
    adapters = [
        AgtxAdapter(),
        BmadAdapter(),
        MattAdapter(),
        SuperpowersAdapter(),
        RtkAdapter(),
        CodeServerAdapter(),
        HerdrAdapter(),
    ]
    adapters.extend(make_agent_adapter(name, hint) for name, hint in _AGENT_SPECS)
    return adapters


def adapters_by_category(include: Iterable[str] | None = None):
    out: dict[str, list] = {}
    for a in registry():
        if include and a.name not in include:
            continue
        cat = getattr(a, "category", "integrations")
        out.setdefault(cat, []).append(a)
    return out
