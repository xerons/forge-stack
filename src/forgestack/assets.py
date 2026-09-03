"""Locates ForgeStack-owned installable assets in the source checkout."""

from pathlib import Path


# ponytail: resolves the repo checkout; wheel installs need importlib.resources/package-data instead.
def asset_root() -> Path:
    return Path(__file__).resolve().parents[2]


def skill_suite_files() -> list[Path]:
    root = asset_root() / "skills" / "forgestack"
    return sorted(p for p in root.rglob("*") if p.is_file())


def plugin_template() -> Path:
    return asset_root() / "agtx" / "plugins" / "forgestack" / "plugin.toml"
