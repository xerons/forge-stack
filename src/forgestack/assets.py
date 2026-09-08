"""Locate ForgeStack-owned assets in a checkout or an installed package."""

from pathlib import Path


def asset_root() -> Path:
    """Return the source checkout root or bundled package-data root."""
    checkout = Path(__file__).resolve().parents[2]
    if (checkout / "skills" / "forgestack").is_dir():
        return checkout

    bundled = Path(__file__).resolve().parent / "_assets"
    if (bundled / "skills" / "forgestack").is_dir():
        return bundled
    raise FileNotFoundError("ForgeStack skill assets are not installed")


def skill_suite_files() -> list[Path]:
    root = asset_root() / "skills" / "forgestack"
    return sorted(p for p in root.rglob("*") if p.is_file())


def plugin_template() -> Path:
    return asset_root() / "agtx" / "plugins" / "forgestack" / "plugin.toml"
