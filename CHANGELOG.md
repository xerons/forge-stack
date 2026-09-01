# Changelog

All notable changes to ForgeStack are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/); versioning follows [SemVer](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-09-01

### Added

- `forgestack` CLI with `setup`, `init`, `agents`, `manager`, `open`, `board`, `status`, `inbox`, `doctor`, `update`, `version`.
- Adapter framework with shared detection (`detect_version`) and registry.
- Adapters for AGTX, BMAD, Matt skills, Superpowers, RTK, code-server, Herdr, Caveman, Tailscale, and agent CLIs (Codex, Claude, OpenCode, Gemini, Antigravity).
- Unified config model (`~/.config/forgestack/config.toml`, `.forgestack.toml`) with deep merge.
- `forgestack init` project bootstrap and `forgestack doctor` diagnostics.
- Dynamic agent routing configuration via `forgestack agents`.
- ForgeStack skill suite (`skills/forgestack/`) and AGTX plugin (`agtx/plugins/forgestack/`).
- Tool manifests (`manifests/tools.toml`, `manifests/compatibility.toml`).
- MIT License.
- Unit and smoke test suites.
- GitHub Actions CI workflow (`.github/workflows/ci.yml`).