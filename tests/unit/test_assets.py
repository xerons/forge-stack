from pathlib import Path

from forgestack import assets
from forgestack.assets import asset_root, plugin_template, skill_suite_files


def test_asset_root_contains_skill_suite():
    assert asset_root().exists()
    assert (asset_root() / "skills" / "forgestack").is_dir()


def test_skill_suite_files_non_empty_and_exist():
    files = skill_suite_files()
    assert files
    assert all(p.is_file() for p in files)
    assert any(str(p).endswith("phase-designer/SKILL.md") for p in files)


def test_plugin_template_exists():
    assert plugin_template().is_file()


def test_bundled_assets_match_checkout_assets():
    repo_root = Path(__file__).resolve().parents[2]
    source_root = repo_root / "skills" / "forgestack"
    bundled_root = repo_root / "src" / "forgestack" / "_assets"
    for source in source_root.rglob("*"):
        if source.is_file():
            target = bundled_root / "skills" / "forgestack" / source.relative_to(source_root)
            assert target.read_bytes() == source.read_bytes()

    source_plugin = repo_root / "agtx" / "plugins" / "forgestack" / "plugin.toml"
    bundled_plugin = bundled_root / "agtx" / "plugins" / "forgestack" / "plugin.toml"
    assert bundled_plugin.read_bytes() == source_plugin.read_bytes()


def test_asset_root_falls_back_to_packaged_assets(tmp_path, monkeypatch):
    package_dir = tmp_path / "site-packages" / "forgestack"
    (package_dir / "_assets" / "skills" / "forgestack").mkdir(parents=True)
    monkeypatch.setattr(assets, "__file__", str(package_dir / "assets.py"))

    assert assets.asset_root() == package_dir / "_assets"
