"""Voiceover with Kokoro (local, offline), one wav per line.

usage: python tts.py vo.json <outdir>
vo.json: {"voice": "am_michael", "speed": 1.18, "lang": "en-us", "lines": ["...", "..."]}
Needs: pip install kokoro-onnx soundfile, and the model files kokoro-v1.0.onnx + voices-v1.0.bin in
GVS_KOKORO_DIR (default ~/.local/share/kokoro-tts). See the README for the one-time download.
"""
import json, os, sys

K = os.path.expanduser(os.environ.get("GVS_KOKORO_DIR", "~/.local/share/kokoro-tts"))
if len(sys.argv) != 3:
    sys.exit("usage: python tts.py vo.json <outdir>")
try:
    import soundfile as sf
    from kokoro_onnx import Kokoro
except ImportError:
    sys.exit("error: voiceover needs `pip install kokoro-onnx soundfile` (see the README), or skip the voiceover.")
model, voices = os.path.join(K, "kokoro-v1.0.onnx"), os.path.join(K, "voices-v1.0.bin")
if not (os.path.isfile(model) and os.path.isfile(voices)):
    sys.exit(f"error: Kokoro model files not found in {K}. Download them once (see the README) or set GVS_KOKORO_DIR.")
k = Kokoro(model, voices)
spec = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
voice, speed, lang = spec["voice"], spec.get("speed", 1.1), spec.get("lang", "en-us")
for i, t in enumerate(spec["lines"]):
    a, sr = k.create(t, voice=voice, speed=speed, lang=lang)
    sf.write(f"{out}/l{i}.wav", a, sr)
    print(i, round(len(a) / sr, 2), t)
