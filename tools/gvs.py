"""Shared settings for the gameplay-vertical-short tools.

Everything machine-specific comes from environment variables, with sensible defaults:

  GVS_FONT        bold .ttf/.otf for captions and covers (default: Impact, else DejaVu Sans Bold)
  GVS_SFX_DIR     folder with your sound-effect files (optional; see sfx.py)
  GVS_KOKORO_DIR  folder with kokoro-v1.0.onnx and voices-v1.0.bin (optional; see tts.py)
  GVS_TONEMAP     auto (default) | hdr | sdr : how to convert the source to SDR bt709
"""
import json
import os
import re
import subprocess
import sys

FONTS = [
    "/System/Library/Fonts/Supplemental/Impact.ttf",                 # macOS
    "C:/Windows/Fonts/impact.ttf",                                   # Windows
    "/usr/share/fonts/truetype/msttcorefonts/Impact.ttf",            # Linux with ttf-mscorefonts
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",          # Debian/Ubuntu fallback
    "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf",        # Fedora fallback
]

# HDR10 / HLG -> SDR bt709 with the Hable curve (keeps highlights, no clipping).
TONEMAP_HDR = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,"
               "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")
TONEMAP_SDR = "format=yuv420p"


def die(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def font() -> str:
    f = os.environ.get("GVS_FONT")
    if f:
        if not os.path.isfile(f):
            die(f"GVS_FONT points to a missing file: {f}")
        return f
    for f in FONTS:
        if os.path.isfile(f):
            return f
    die("no caption font found; set GVS_FONT to a bold .ttf (e.g. Impact or DejaVu Sans Bold)")


def is_hdr(src: str) -> bool:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=color_transfer", "-of", "json", src], capture_output=True, text=True).stdout
    try:
        trc = json.loads(out)["streams"][0].get("color_transfer", "")
    except (ValueError, KeyError, IndexError):
        return False
    return trc in ("smpte2084", "arib-std-b67")


def tonemap(src: str) -> str:
    mode = os.environ.get("GVS_TONEMAP", "auto").lower()
    hdr = is_hdr(src) if mode == "auto" else mode == "hdr"
    return TONEMAP_HDR if hdr else TONEMAP_SDR


def normalize_1080p() -> str:
    """Any 16:9-ish source -> 1920x1080 (a PS5 1920x1088 frame keeps its top 1080 rows, as before)."""
    return "scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1920:1080:0:0"


def _ffmpeg_major() -> int:
    out = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True).stdout
    m = re.search(r"ffmpeg version n?(\d+)", out)
    return int(m.group(1)) if m else 7


def filter_script_args(path: str) -> list:
    """Read a filter graph from a file: `-/filter_complex` on ffmpeg 7+, the old option before that."""
    return ["-/filter_complex", path] if _ffmpeg_major() >= 7 else ["-filter_complex_script", path]
