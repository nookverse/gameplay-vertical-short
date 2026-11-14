# Changelog

All notable changes are documented here, following [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Fixed
- HDR sources on an ffmpeg without `zscale` now stop with a clear install hint; SDR sources never need it.
- The smoke test and CI check each required filter separately and use an SDR source when `zscale` is missing.

## [1.0.0] - 2026-11-14

First public release.

### Added
- `SKILL.md`: the full scan → plan → render → sound → cover → publish-kit workflow and quality rules.
- Tools: `grab.py`, `render_glow.py`, `tts.py`, `build_vo.py`, `score.py`, `sfx.py`, `mix.sh`,
  `cover_glow.py`, `cover_first.sh`, and shared settings in `gvs.py`.
- Automatic HDR detection (HDR10/HLG tone-mapped, SDR passed through) and any 16:9 source size.
- Optional voiceover and sound effects (silent tracks when absent); HUD minimap is opt-in, with a
  Call of Duty preset and `minimap_box` for other games.
- `install.sh` for Claude Code, Codex and shared agent skill folders (backs up existing copies).
- Examples, an end-to-end smoke test and CI on macOS and Linux.
