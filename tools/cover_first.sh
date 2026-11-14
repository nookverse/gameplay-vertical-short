#!/bin/bash
# cover_first.sh <in.mp4> <cover.jpg> <out.mp4> [seconds=0.4]
# Puts the cover/thumbnail on screen for the first few frames (no timing change, audio copied),
# so the video's first frame = the thumbnail (never a white flash frame).
IN="$1"; COV="$2"; OUT="$3"; D="${4:-0.4}"; mkdir -p "$(dirname "$OUT")"
ffmpeg -v error -y -i "$IN" -loop 1 -framerate 60 -t "$D" -i "$COV" -filter_complex \
 "[1:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,format=yuv420p,setsar=1[c];[0:v][c]overlay=0:0:eof_action=pass:enable='lt(t,$D)'[v]" \
 -map "[v]" -map 0:a -c:v libx264 -preset slow -crf 14 -profile:v high -pix_fmt yuv420p \
 -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv -r 60 \
 -c:a copy -movflags +faststart "$OUT"
