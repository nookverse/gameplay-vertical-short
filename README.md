# Gameplay → Vertical Short

**An agent skill that turns a full gameplay recording into a polished vertical short for YouTube
Shorts, TikTok, Instagram and Facebook Reels.**

[![CI](https://github.com/nookverse/gameplay-vertical-short/actions/workflows/ci.yml/badge.svg)](https://github.com/nookverse/gameplay-vertical-short/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Agent Skill](https://img.shields.io/badge/agent-skill-8A2BE2)

Give your AI agent a recording and say *"make a short of this"*. The agent watches the footage
(contact sheets and full-resolution frames), finds the story, fact-checks every caption against what's
on screen, and drives the small ffmpeg/Python tools in this repo to produce:

- a **1080×1920, 60 fps** video with a **blurred background and a sharp gameplay band** (no border lines)
- **glowing, multi-colour gradient captions**, zoom punches, shake, glitch, slow-mo with motion interpolation
- a live **HUD minimap** copy for games that have one (Call of Duty DMZ/Warzone preset included)
- an **original procedural score** (no samples, no copyrighted music), **sound effects** and an optional
  **local AI voiceover** (Kokoro)
- a **glowing cover** that is also the video's first frame
- a **copy-ready publish kit** for YouTube Shorts, TikTok and Instagram + Facebook Reels

Everything runs locally. Nothing is uploaded or posted for you.

> Want a fully automatic edit in one call instead? Use [NookCut](https://github.com/nookverse/nookcut),
> an offline MCP server. This skill is the hand-crafted, highest-quality path.

## Contents

- [How it works](#how-it-works)
- [Requirements](#requirements)
- [Install](#install)
- [Configuration](#configuration)
- [Use it](#use-it)
- [The tools](#the-tools)
- [Project folder](#project-folder)
- [Privacy](#privacy)
- [FAQ](#faq) · [Contributing](#contributing) · [License](#license)

## How it works

The skill (`SKILL.md`) is a playbook for the agent. It tells the agent to:

1. **Scan.** Make time-stamped contact sheets of the whole clip, zoom in on key moments, and read
   loot cards and HUD text from full-resolution frames.
2. **Plan.** Shape the story (hook → setup → build-up → reveal → payoff → question) in `segs.json`,
   with speed, zoom, captions and effects per segment.
3. **Render.** Tone-map HDR to SDR automatically, then render each segment, cached so edits re-render
   only what changed.
4. **Sound.** Add the voiceover (optional), a score with drops on the reveals, sound effects on the
   cuts, and mix to −14 LUFS.
5. **Cover.** Make a glowing cover and put it on frame 0.
6. **Publish kit.** Write titles, captions, hashtags, a pinned comment and an estimated posting time.

The agent also follows the house rules: facts only from frames it actually looked at, no weapon
level-up pop-ups, no border lines (Facebook penalizes them), keep old versions, never post.

## Requirements

- **ffmpeg** with `drawtext`, `gradients`, `zoompan` and `minterpolate` (ffmpeg 6.1+; 7+ recommended), plus
  `zscale` (libzimg) for **HDR** captures such as PS5 HDR. SDR footage doesn't need it.
  - macOS: `brew install ffmpeg-full`, then put it on your PATH (it's keg-only):
    `echo 'export PATH="$(brew --prefix ffmpeg-full)/bin:$PATH"' >> ~/.zprofile`. Homebrew's plain
    `ffmpeg` is a minimal build without `drawtext` (captions) or `zscale` (HDR).
  - Debian/Ubuntu: `sudo apt install ffmpeg fonts-dejavu-core`
  - Windows: `winget install Gyan.FFmpeg` (see the [FAQ](docs/FAQ.md#does-it-work-on-windows))
- **Python 3.10+** with `numpy`, `scipy` and `soundfile` for the score: `pip install -r requirements.txt`
- **An agent that supports skills**, such as Claude Code, Codex or any agent that can read a Markdown
  playbook and run shell commands
- Optional: **Kokoro** for the voiceover (`pip install kokoro-onnx` plus two model files, see below)
- Optional: a **sound-effects library**, such as Blackmagic Design's free Fairlight Sound Library or your own files

Check your ffmpeg (you should see all five; `zscale` only matters for HDR):

```bash
ffmpeg -hide_banner -filters | grep -E "^ *[^ ]+ +(drawtext|zscale|gradients|zoompan|minterpolate) "
```

## Install

```bash
git clone https://github.com/nookverse/gameplay-vertical-short.git
cd gameplay-vertical-short
python3 -m pip install -r requirements.txt
./install.sh                 # Claude Code (~/.claude/skills); also: --codex, --agents, or --dir <path>
```

`install.sh` copies `SKILL.md`, `tools/` and `examples/` into the skills folder. If a skill with the
same name is already there, it's moved to `~/.local/share/gameplay-vertical-short/backups/` first (outside
the skills folder, so it isn't loaded twice), never overwritten.

**Voiceover (optional, one-time download, about 340 MB):**

```bash
python3 -m pip install kokoro-onnx soundfile
mkdir -p ~/.local/share/kokoro-tts && cd ~/.local/share/kokoro-tts
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
```

After that, the voiceover works offline.

## Configuration

All optional. Set them in your shell profile or tell your agent.

| Variable | Default | Purpose |
|---|---|---|
| `GVS_FONT` | Impact, else DejaVu Sans Bold | Bold font for captions and covers |
| `GVS_SFX_DIR` | none | Folder with your sound effects (Fairlight's `Media Files` folder matches the built-in keys) |
| `GVS_KOKORO_DIR` | `~/.local/share/kokoro-tts` | Folder with the Kokoro model files |
| `GVS_PYTHON` | `python3` | Python that has numpy/scipy/soundfile (and kokoro-onnx) installed |
| `GVS_TONEMAP` | `auto` | `auto` detects HDR10/HLG; force with `hdr` or `sdr` |

Fill in the **Creator profile** at the top of `SKILL.md` (channel name, handle, audience regions,
folders), or let the agent ask you the first time.

## Use it

Ask your agent, for example:

> Make a vertical short from `~/Videos/raw/match-0412.webm`. We finally extracted with the legendary
> case after three failed runs, around 12:40.

The agent asks for anything missing, shows you what it found, renders, checks the frames, and hands
you the video, the cover and `social_posts.md`. You review it and post it yourself.

## The tools

| Tool | What it does |
|---|---|
| `tools/grab.py` | One tone-mapped frame, or a time-stamped contact sheet |
| `tools/render_glow.py` | Main renderer: layout, glowing captions, zoom/punch/shake/glitch, slow-mo, minimap, progress bar |
| `tools/tts.py` | Kokoro voiceover, one wav per line |
| `tools/build_vo.py` | Places voice lines at their segments; writes `vo.wav` and `times.json` |
| `tools/score.py` | Procedural score with sections, drops, risers and stops |
| `tools/sfx.py` | Places sound effects by key or file path |
| `tools/mix.sh` | Final mix: game audio and score ducked under the voice, −14 LUFS, stems saved |
| `tools/cover_glow.py` | Glowing 1080×1920 cover from a JSON spec |
| `tools/cover_first.sh` | Shows the cover for the first 0.4 s so frame 0 is the thumbnail |

Example inputs for each step are in [`examples/`](examples). `tests/smoke.sh` runs the whole chain on
synthetic footage.

## Project folder

```
<slug>/
  short/<seo-name>.mp4         the finished video
  short/stems/{vo,score,sfx}.wav
  thumbnails/shorts-reels-thumbnail.jpg
  social_posts.md              publish kit
  work/a/{segs.json, vo.json, score.json, sfx.json, video.mov, seg_*.mov}
  work/sheet/  work/hi/        contact sheets and full-resolution frames
```

## Privacy

- No network calls. The only download is the optional Kokoro model, which you run yourself.
- Nothing is uploaded or posted.
- The skill tells the agent to keep your console or platform ID and other private details out of
  the crop, captions and cover.

## FAQ

See **[docs/FAQ.md](docs/FAQ.md)**.

## Contributing

Issues and pull requests are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md) and the
[Code of Conduct](CODE_OF_CONDUCT.md). Report security problems privately ([SECURITY.md](SECURITY.md)).

## License

[MIT](LICENSE) © 2026 Nookverse. Game names are trademarks of their owners; this project isn't
affiliated with any game publisher or platform.
