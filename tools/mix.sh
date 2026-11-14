#!/bin/bash
# mix.sh <workdir> <out.mp4>
# Final audio mix for a short. Needs in <workdir>: video.mov (picture + game audio), vo.wav, score.wav, sfx.wav.
# Game audio and score are side-chain ducked under the voiceover; loudness -14 LUFS, true peak < -1 dB.
# Video stream is copied (no re-encode). Stems are copied next to the output in stems/.
W="$1"; OUT="$2"; mkdir -p "$(dirname "$OUT")"
ffmpeg -v error -y -i "$W/video.mov" -i "$W/vo.wav" -i "$W/score.wav" -i "$W/sfx.wav" -filter_complex "
[1:a]aformat=channel_layouts=stereo,asplit=3[vo][k1][k2];
[0:a]aresample=48000,aformat=channel_layouts=stereo,volume=2dB[g];[g][k1]sidechaincompress=threshold=0.03:ratio=6:attack=10:release=250[gd];
[2:a]aformat=channel_layouts=stereo,volume=-3dB[s];[s][k2]sidechaincompress=threshold=0.03:ratio=4:attack=10:release=300[sd];
[3:a]aformat=channel_layouts=stereo,volume=5dB[fx];
[vo][gd][sd][fx]amix=inputs=4:normalize=0,acompressor=threshold=-18dB:ratio=2.5:makeup=2,alimiter=limit=0.9:level=0,loudnorm=I=-14:TP=-2:LRA=9,aresample=192000,alimiter=limit=0.7:level=0,aresample=48000[a]" \
 -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 256k -movflags +faststart -shortest "$OUT" || exit 1
mkdir -p "$(dirname "$OUT")/stems"; cp "$W/vo.wav" "$W/score.wav" "$W/sfx.wav" "$(dirname "$OUT")/stems/"
ffprobe -v error -show_entries format=duration,bit_rate:stream=width,height,r_frame_rate -of compact "$OUT"
ffmpeg -nostats -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I:|Peak:)"
