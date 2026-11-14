# FAQ

## General

### What is this?
An agent skill: a playbook (`SKILL.md`) plus small tools that let an AI agent edit a gameplay
recording into a finished vertical short. The agent does the looking and planning; the tools do the
rendering and audio.

### Which agents can use it?
Any agent that can read a Markdown playbook and run shell commands: Claude Code (as a skill), Codex,
and others that support the `SKILL.md` format or can be pointed at the file. `install.sh` handles
the common skill folders.

### Which games does it work with?
Any game. The defaults are tuned for shooters with loot reveals (Call of Duty DMZ/Warzone), and the
HUD minimap preset fits Call of Duty. For other games, leave `minimap` off or set `minimap_box` to
where that game draws its minimap.

### Which capture formats?
Anything ffmpeg reads (`.webm`, `.mp4`, `.mov`, `.mkv`) at 16:9. PS5 HDR captures (VP9 HDR10,
1920×1088) are detected and tone-mapped automatically; SDR captures pass straight through. 4K is
scaled to 1080p.

### How is this different from NookCut?
[NookCut](https://github.com/nookverse/nookcut) is an MCP server that makes a short automatically,
in one call, from any kind of video. This skill is a slower, hands-on workflow where the agent
inspects frames, writes fact-checked captions and builds richer effects, a voiceover and a custom
cover. Use NookCut for speed and this skill for showcase videos.

## Output

### Will the music get copyright claims?
The score is synthesized from scratch by `score.py`, with no samples or existing recordings, so
there's no source track to match. Automated systems occasionally misfire on original music; if that
happens, dispute the claim. Don't add copyrighted songs; trending sounds belong in the platform's app.

### Where do the sound effects come from?
Your own library. Point `GVS_SFX_DIR` at a folder of sounds. The built-in key names (`impact`,
`whoosh`, `locker`, ...) match Blackmagic Design's free Fairlight Sound Library, but you can use any
file by absolute path. No sound effects ship with this repo. With an empty `sfx.json` you get a
silent effects track.

### Do I need the voiceover?
No. Without `vo` keys in `segs.json`, `build_vo.py` writes a silent track and the mix works as usual.
To use it, install `kokoro-onnx` and download the two model files once (see the README). After that,
it runs offline.

### Why no border around the gameplay?
Facebook flags framed footage ("Your video has a border") and reduces its reach, so the sharp band
sits directly on the blurred background.

### Why is the cover on the first frame?
Several platforms pick or show the first frame as the thumbnail. `cover_first.sh` puts the cover on
screen for the first 0.4 s, so the thumbnail is always the cover, never a white or random frame.

### What loudness does it target?
−14 LUFS integrated with true peak below −1 dB, the common target for YouTube, TikTok and Instagram.

## Troubleshooting

### `No such filter: 'gradients'`, or "converting it needs ffmpeg's zscale filter"
Your ffmpeg build lacks them. `zscale` is only needed for HDR captures. Install a full build: on
Debian/Ubuntu `apt install ffmpeg` includes both. On macOS, Homebrew's plain `ffmpeg` is a minimal
build: install `ffmpeg-full` and put `$(brew --prefix ffmpeg-full)/bin` first on your PATH. On Windows, use a full static build.

### `no caption font found`
Set `GVS_FONT` to a bold `.ttf`, for example DejaVu Sans Bold on Linux (`apt install fonts-dejavu-core`).

### The colours look washed out or too dark
The source's HDR flag may be wrong. Force the conversion with `GVS_TONEMAP=hdr` or `GVS_TONEMAP=sdr`.

### A segment didn't change after I edited it
Segments are cached by a hash of their settings. If you changed something outside `segs.json`
(the source file, the font), delete the `work/a/seg_*.mov` files and render again.

### Does it work on Windows?
The Python tools do. `mix.sh`, `cover_first.sh`, `install.sh` and `tests/smoke.sh` need a bash
shell (Git Bash or WSL). CI covers macOS and Linux only.

### Where do I report a bug?
[Open an issue](https://github.com/nookverse/gameplay-vertical-short/issues). Report security
problems privately (see [SECURITY.md](../SECURITY.md)).

## Legal

### Can I post videos made with this?
The tools and the score are yours to use (MIT). The gameplay footage is subject to the game
publisher's content and streaming policies; most publishers allow gameplay videos, but check yours.
This project isn't affiliated with any game publisher or platform.
