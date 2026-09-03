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
