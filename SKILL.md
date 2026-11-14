---
name: gameplay-vertical-short
description: Turn a full-length gameplay recording (PS5/Xbox/PC captures, HDR or SDR; tuned for shooters like Call of Duty DMZ/Warzone but works for any game) into a finished vertical short for YouTube Shorts, TikTok, Instagram and Facebook Reels - finding the moments, fact-checked captions, glowing multi-colour text, optional hype voiceover, an original score, sound effects, HUD minimap, a cover and a copy-ready publish kit. Use whenever the user drops a gameplay .webm/.mp4/.mov and asks for a short, reel, clip, vertical video or "make a video of this", even if they only describe what happened in the match.
---

# Gameplay → vertical short

A hand-crafted, highest-quality pipeline: you (the agent) look at the footage, plan every segment,
and drive small ffmpeg/Python tools that ship with this skill in `tools/` (next to this file; call
that folder `$T` below). Everything runs locally. Nothing is uploaded or posted.

For a fully automatic cut in one call, the [NookCut](https://github.com/nookverse/nookcut) MCP server
is the quick path. This skill is for when quality and storytelling matter most.

## Creator profile (fill in once, or ask the user)

- Channel / brand name: `<ask the user>`
- Handle for captions and the publish kit: `<ask the user>`
- Audience regions (for posting times and language): `<ask the user, e.g. US / EU / AU>`
- Where recordings are and where outputs go: `<ask the user>`; default output folder `./social-contents/<slug>/`

Never put the user's private details (real name, PSN/Xbox/Steam ID, email) in captions, titles or
covers unless they ask.

## Hard rules

1. **Vertical only** (1080x1920, 60 fps) unless asked otherwise.
2. **Source quality.** HDR captures (HDR10/HLG, e.g. PS5 VP9 at 1920x1088) are tone-mapped to SDR
   bt709 automatically (Hable curve); SDR sources pass straight through. Encode x264 **crf 14**,
   preset slow, high profile, tagged bt709. When only the audio changes, remix with `-c:v copy`.
3. **Layout = blurred background + sharp gameplay band** (1296x1080 crop → 1080x900 at y=470).
   **No border lines, frames or boxes around the sharp footage** (Facebook flags "Your video has a
   border" and cuts reach). Not full-bleed unless the user asks.
4. **HUD minimap** in the lower blurred area for games that have one: set `"minimap": true` on
   segments where the minimap is on screen (the default box fits Call of Duty; use `minimap_box` for
   other games). Leave it off for full-map screens, inventory, menus, summaries and cutscenes.
5. **Captions glow in multiple cool colours**: gradient fill, dark stroke and a two-layer coloured
   glow, with a different palette per shot (`neon toxic sunset ultra ice violet`; `ultra` or `gold`
   for legendary reveals).
6. **Voiceover (optional)** = Kokoro `am_michael`, hype gamer tone, speed ~1.15–1.2. Never robotic
   system voices. Skip it if Kokoro isn't installed and say so.
7. **Sound effects** from the user's own library (`GVS_SFX_DIR`; Blackmagic's free Fairlight Sound
   Library, a separate free download from Blackmagic Design, matches the built-in keys), plus the procedural score. **No
   copyrighted music.**
8. **First frame = the thumbnail.** The last step is always `cover_first.sh` (cover shown for the
   first 0.4 s). Frame 0 must never be white.
9. **Don't show weapon level-up or "NEW UNLOCK" pop-ups** unless asked.
10. **Facts only from the footage.** Every caption and voiceover claim (item names, rarity,
    locations, prices) must be read off a frame you actually looked at. If the user's description
    differs from the screen (e.g. "safe" vs a "rifle case"), caption what the screen shows and tell
    the user. Web facts get a source; anything unverified is hedged or left out.
11. **Never upload or post.** Install nothing without asking. Keep previous versions when re-doing
    ("make a new version, keep the old one").
12. **Publish kit:** one combined Instagram + Facebook post (not two). Each caption block must be
    copy-ready on its own; put pinned comments and notes in clearly separate sections so they never
    get pasted into a caption.

## Setup check (first run)

```bash
ffmpeg -hide_banner -filters | grep -E " (zscale|gradients|zoompan|minterpolate) "   # all four needed
python3 -c "import numpy, scipy, soundfile"        # for the score (pip install -r requirements.txt)
python3 -c "import kokoro_onnx"                    # only for voiceover
```

If something is missing, show the user the install command from the README and wait. `GVS_FONT`
sets the caption font (Impact by default, DejaVu Sans Bold as fallback).

## Workflow

Track steps in a task list, and during long renders tell the user briefly what you're doing.

### 1. Probe and scan
```bash
ffprobe -v error -show_entries format=duration:stream=width,height,color_transfer -of compact "$SRC"
python3 $T/grab.py --sheet "$SRC" START LEN FPS work/sheet/s_START.jpg   # time-stamped contact sheet
python3 $T/grab.py "$SRC" T work/hi/h_T.png 0                            # full-res frame (cards, covers)
```
Scan the whole clip every 2–5 s, then 0.25–0.5 s around key moments, then grab full-resolution
frames of every loot card or banner you'll caption. Loot cards often stay up < 1 s, so sample at
4–10 fps and note exact in/out times. Crop the HUD (objectives, location, squad) to read text. If the
user gives timestamps, start there but still verify.
**zsh gotcha:** never write `$F:textfile` / `$5:c1` in filter strings (zsh `:t`/`:c` modifiers); use `${F}`.

### 2. Research (optional, web)
Only if the user allows it and you have web search: item/key/location names, what they unlock, the
current meta, the game's newest season. Note where guides conflict. Use what's verified and cite
sources in the final message.

### 3. Plan segments → `work/a/segs.json`
Story shape (≈25–60 s): **hook (best moment: slow-mo, punch/shake/glitch, flash)** → setup →
build-up → reveal(s) (slow-mo 0.3–0.5x on cards, zoomed crop) → payoff/secure/exfil → end card with
a comment question (fadeout). Speed up dull travel 2–10x. See `examples/segs.example.json`.

Keys per segment (`render_glow.py`): `in, out, speed, top ("LINE1|LINE2", ≤ ~14 chars/line),
bottom (≤ ~30 chars), pal, cx/cy/zw (zoom: zw 520–1000 crop width; centre the card), push,
punch (0.1–0.3), shake (px), glitch, flash, fadeout, nofade, minimap, minimap_box, vo (line index),
file (a pre-rendered 1080x1920 clip)`.
Cards usually sit around x 500–850 of the 1920 frame: set cx/cy/zw so the card and its panel are
inside the crop. Keep the player's on-screen ID out of the crop (on PS5 it's at the bottom-left of
the HUD: keep cx ≥ ~312 or crop above y≈1040).
Map moments: build an animated zoom (`zoompan` on a still map frame + a pulsing `geq` ring + labels)
as a `file` segment.

### 4. Voiceover (optional)
`work/a/vo.json` = `{"voice":"am_michael","speed":1.18,"lines":[...]}`. Write short, punchy hype
lines, one per `vo` segment, and spell tricky names phonetically ("point five seven", "D R C").
```bash
$GVS_PYTHON $T/tts.py work/a/vo.json work/a/vo
```
Each line must fit its segment (plus the next segment if that one has no VO); check durations and
adjust speeds or lines.

### 5. Render picture + place VO
```bash
SRC="$SRC" python3 $T/render_glow.py work/a work/a/video.mov
python3 $T/build_vo.py work/a        # writes vo.wav (silent if no VO) + times.json (segment starts)
```
Segments are cached by a hash of their settings: edit one, re-run, and only that one re-renders.
Run long renders in the background. **Check the frames**: grab one frame per segment into a strip
and look at it (captions fit the width, card readable, no wrong card, nothing clipped). Fix and
re-render before the audio.

### 6. Score + SFX + mix
`score.json`: `{"total":T,"bpm":140-150,"sections":[[a,b,level 0-3]],"drops":[reveal times],"risers":[...],"stops":[[t-0.4,t]]}`.
Put silence right before the biggest reveal and the drop on it.
`sfx.json`: `[[time,"key or /abs/file.wav",length,gain_dB],...]`. Put a whoosh on every cut
(t-0.05) and an impact + low whoosh on reveals, plus foley that matches the action (keys, lock,
locker, zip, rummage, cock, jeep, body fall).
Built-in keys (with the Fairlight library): impact whoosh lowwhoosh cardoor jeep keys keyslight lock
latch locker hiss zip rummage cock gear catwalk toolbox map. An empty list gives a silent track.
```bash
$GVS_PYTHON $T/score.py work/a/score.json work/a/score.wav
python3 $T/sfx.py work/a/sfx.json TOTAL work/a/sfx.wav
$T/mix.sh work/a <slug>/short/<seo-name>.tmp.mp4     # -14 LUFS, true peak < -1 dB, video copied
```

### 7. Cover (glowing style)
Write a spec JSON for `cover_glow.py` (see its docstring and `examples/cover.example.json`): a sharp
darkened background slice, a soft colour glow, 1–2 tilted UI cards with coloured borders (the hero
item big), an optional round inset (scope/minimap/locker slot) with a ring, a glowing gradient
headline (2–4 words) plus a sub-line and location line, and a neon strip. Check that no text
clips the 1080 width.
```bash
python3 $T/cover_glow.py cover.json      # -> <slug>/thumbnails/shorts-reels-thumbnail.jpg
```

### 8. Cover as first frame (always last)
```bash
$T/cover_first.sh <slug>/short/<name>.tmp.mp4 <slug>/thumbnails/shorts-reels-thumbnail.jpg <slug>/short/<name>.mp4 && rm <slug>/short/<name>.tmp.mp4
```
Verify that frame 0 is the cover and that the duration and loudness didn't change.

### 9. Publish kit → `<slug>/social_posts.md`
Start with what the footage shows (with timestamps). Then:
- **YouTube Shorts**: a title of ≤ 70 chars with the game + item/boss + hook, a description, 5–8 hashtags.
- **TikTok** caption.
- **Instagram + Facebook Reels** caption (one post).
- **Pinned comment** (its own section).
- Wording notes: what was verified and what was hedged.
- Best posting time for the audience's region, labelled as an estimate.

Facebook advice to include: upload natively (not via Instagram auto-share), fill in the title, and
share to 2–3 game groups.

### 10. Hand over
Give the user the video and the cover. The final message covers:
- what the footage shows (timestamps) and the edit structure
- the quality: 1080x1920 60 fps, bitrate, LUFS/peak
- any facts that differ from the user's description, with sources
- that you checked frames and loudness but didn't listen, so they should play it once before posting

## Quality checklist before handing over
- [ ] Every caption/VO fact matches a frame you looked at
- [ ] No weapon level-up pop-ups; no border lines around footage; minimap only where the HUD shows it
- [ ] Captions inside 1080 px; VO lines don't overlap
- [ ] 1080x1920, 60 fps, ~10–15 Mbps, −14 LUFS ±0.5, peak ≤ −1 dB
- [ ] Frame 0 = cover
- [ ] Old versions kept; nothing uploaded; no private IDs on screen
