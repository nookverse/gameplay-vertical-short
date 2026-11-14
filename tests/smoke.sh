#!/usr/bin/env bash
# End-to-end check on synthetic footage: frames, render, voiceover placement, score, SFX, mix, cover, cover-first.
#   tests/smoke.sh [workdir]        (needs ffmpeg with zscale + gradients, and python3 with numpy scipy soundfile)
set -euo pipefail
T="$(cd "$(dirname "$0")/../tools" && pwd)"
D="${1:-$(mktemp -d)}"; mkdir -p "$D/work/a" "$D/work/hi" "$D/thumbnails" "$D/short"
PY="${GVS_PYTHON:-python3}"
echo "workdir: $D"

# 1. a 20 s HDR10-tagged clip (PQ / bt2020), like a console capture, plus a test hit sound
ffmpeg -v error -y -f lavfi -i "testsrc2=s=1920x1080:r=60:d=20" -f lavfi -i "sine=f=330:d=20" \
  -vf "format=yuv420p10le,setparams=color_primaries=bt2020:color_trc=smpte2084:colorspace=bt2020nc" \
  -c:v libx265 -preset ultrafast -x265-params log-level=error -c:a aac "$D/src.mp4"
ffmpeg -v error -y -f lavfi -i "sine=f=80:d=1.5" "$D/hit.wav"
SRC="$D/src.mp4"

# 2. frames and a contact sheet
python3 "$T/grab.py" "$SRC" 5 "$D/work/hi/h_5.png" 0 >/dev/null
python3 "$T/grab.py" --sheet "$SRC" 0 10 1 "$D/work/sheet.jpg" >/dev/null

# 3. render (slow-mo + punch + glitch + flash, fast-forward + minimap, zoomed crop, fade-out)
cat > "$D/work/a/segs.json" <<JSON
[{"in": 2.0, "out": 3.6, "speed": 0.5, "top": "TEST|HOOK", "bottom": "WAIT FOR IT", "pal": "ultra", "punch": 0.25, "shake": 8, "glitch": true, "flash": true},
 {"in": 4.0, "out": 12.0, "speed": 4, "top": "FAST", "pal": "neon", "minimap": true},
 {"in": 13.0, "out": 15.0, "speed": 1, "top": "ZOOM", "pal": "sunset", "cx": 520, "cy": 180, "zw": 760},
 {"in": 16.0, "out": 18.0, "speed": 1, "top": "THE END?", "bottom": "COMMENT BELOW", "pal": "violet", "fadeout": true}]
JSON
SRC="$SRC" python3 "$T/render_glow.py" "$D/work/a" "$D/work/a/video.mov" >/dev/null
python3 "$T/build_vo.py" "$D/work/a" >/dev/null          # no "vo" keys -> silent voiceover track
TOTAL=$(python3 -c "import json;print(json.load(open('$D/work/a/times.json'))['total'])")

# 4. score, SFX, mix
echo "{\"total\": $TOTAL, \"bpm\": 145, \"sections\": [[0, 3, 2], [3, 5, 1], [5, $TOTAL, 3]], \"drops\": [5.0], \"risers\": [5.0], \"stops\": [[4.6, 5.0]]}" > "$D/work/a/score.json"
"$PY" "$T/score.py" "$D/work/a/score.json" "$D/work/a/score.wav" >/dev/null
echo "[[0.0, \"$D/hit.wav\", 1.2, -3], [5.0, \"$D/hit.wav\", 1.0, -6]]" > "$D/work/a/sfx.json"
python3 "$T/sfx.py" "$D/work/a/sfx.json" "$TOTAL" "$D/work/a/sfx.wav" >/dev/null
"$T/mix.sh" "$D/work/a" "$D/short/test.tmp.mp4" >/dev/null

# 5. cover and cover-as-first-frame
cat > "$D/cover.json" <<JSON
{"out": "$D/thumbnails/cover.jpg", "bg": {"img": "$D/work/hi/h_5.png", "x": 600},
 "glow": {"color": "0xFFB000", "x": -60, "y": 330},
 "cards": [{"img": "$D/work/hi/h_5.png", "crop": [285, 305, 537, 207], "w": 600, "x": 40, "y": 470, "rot": -0.05, "border": "0xFFD27A"}],
 "texts": [{"text": "SMOKE TEST", "size": 150, "y": 30, "pal": "ultra", "bw": 10}], "strip": true}
JSON
python3 "$T/cover_glow.py" "$D/cover.json" >/dev/null
"$T/cover_first.sh" "$D/short/test.tmp.mp4" "$D/thumbnails/cover.jpg" "$D/short/test.mp4"

# 6. checks
INFO=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate -of csv=p=0 "$D/short/test.mp4")
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$D/short/test.mp4")
LUFS=$(ffmpeg -nostats -i "$D/short/test.mp4" -af ebur128 -f null - 2>&1 | awk '/I:/{v=$2} END{print v}')
echo "video: $INFO, ${DUR}s, ${LUFS} LUFS (expected ${TOTAL}s)"
[ "$INFO" = "1080,1920,60/1" ] || { echo "FAIL: expected 1080x1920 at 60 fps"; exit 1; }
python3 -c "import sys; d,t=float('$DUR'),float('$TOTAL'); sys.exit(abs(d-t)>0.2)" || { echo "FAIL: duration"; exit 1; }
python3 -c "import sys; sys.exit(abs(float('$LUFS')+14)>1.5)" || { echo "FAIL: loudness"; exit 1; }
echo OK
