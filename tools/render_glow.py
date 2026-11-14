"""Vertical gaming-short renderer with neon multi-colour glowing captions.

usage: SRC=<clip> python3 render_glow.py <workdir> <out.mov>
Any 16:9 source works; HDR (HDR10/HLG, e.g. PS5 captures) is tone-mapped to SDR bt709 automatically.
segs.json keys per segment:
  in, out, speed            source range and speed (<1 = slow-mo, motion-interpolated)
  top ("A|B"), bottom       captions; top up to 2 lines, bottom 1 line
  pal                       palette name (see PAL) for the glowing gradient captions
  cx, cy, zw                foreground crop (default 312, 0, 1296 wide)
  push                      slow zoom-in amount over the segment (default 0.06)
  punch                     zoom punch at segment start, e.g. 0.25 (settles in 0.3 s)
  shake                     camera shake pixels for the first 0.4 s
  glitch                    RGB-split glitch for the first 0.15 s
  flash, fadeout            white flash in / fade to black out
  minimap                   true to copy the HUD minimap into the lower blurred area (off by default).
                            The default region fits Call of Duty (DMZ/Warzone); set "minimap_box": [w, h, x, y]
                            in 1920x1080 coordinates for other games.
  file                      pre-rendered 1080x1920 clip used as-is (still give in/out/speed)
No border lines around the gameplay band (Facebook flags them). A thin progress bar in the palette colour runs along the top across the whole video.
"""
import subprocess, sys, os, json, hashlib
from gvs import die, filter_script_args, font, normalize_1080p, tonemap

if len(sys.argv) != 3 or "SRC" not in os.environ:
    die("usage: SRC=<clip> python3 render_glow.py <workdir> <out.mov>")
SRC = os.environ["SRC"]
if not os.path.isfile(SRC):
    die(f"source not found: {SRC}")
W = sys.argv[1]; OUT = sys.argv[2]
F = font()
TM = tonemap(SRC) + "," + normalize_1080p()
COD_MINIMAP = [262, 244, 14, 38]  # w, h, x, y of the Call of Duty HUD minimap in a 1920x1080 frame
PAL = {  # gradient stops
    "neon":   ["0x00F0FF", "0xFF2BD6", "0x7A5CFF"],
    "toxic":  ["0x39FF14", "0x00F0FF", "0xB6FF00"],
    "sunset": ["0xFF7A00", "0xFF2B8A", "0xFFD400"],
    "ultra":  ["0xFF1E3C", "0xFFB000", "0xFF5A00"],
    "ice":    ["0x7DF9FF", "0xFFFFFF", "0x3D7BFF"],
    "violet": ["0xB04BFF", "0x00E5FF", "0xFF4BD8"],
}
segs = json.load(open(f"{W}/segs.json"))
durs = [(s["out"] - s["in"]) / s["speed"] for s in segs]
starts = [sum(durs[:i]) for i in range(len(durs))]
TOT = sum(durs)


def textlayer(s, i, dur, inner):
    """drawtext chain producing a white-on-black mask (inner = no border)."""
    ch = []
    bw = 0 if inner else 9
    lines = [x for x in s.get("top", "").split("|") if x]
    for j, l in enumerate(lines):
        p = f"{W}/g{i}_{j}.txt"; open(p, "w").write(l)
        ch.append(f"drawtext=fontfile={F}:textfile={p}:fontsize=124:fontcolor=white:borderw={bw}:bordercolor=white:x=(w-text_w)/2:y={140 + j * 145}")
    if s.get("bottom"):
        p = f"{W}/gb{i}.txt"; open(p, "w").write(s["bottom"])
        ch.append(f"drawtext=fontfile={F}:textfile={p}:fontsize=66:fontcolor=white:borderw={max(0, bw - 3)}:bordercolor=white:x=(w-text_w)/2:y=1430")
    return ",".join(ch) if ch else "null"


parts = []
for i, s in enumerate(segs):
    if "file" in s:
        parts.append(s["file"]); print("file", i, flush=True); continue
    a, b, sp = s["in"], s["out"], s["speed"]; dur = durs[i]
    key = {k: v for k, v in s.items() if k != "vo"}; key["_st"] = round(starts[i], 3); key["_tot"] = round(TOT, 3); key["_v"] = 6
    o = f"{W}/seg_" + hashlib.md5(json.dumps(key, sort_keys=True).encode()).hexdigest()[:10] + ".mov"
    if os.path.exists(o):
        parts.append(o); print("cached", i, flush=True); continue
    pal = PAL[s.get("pal", "neon")]
    N = max(1, int(round(dur * 60)))
    push = s.get("push", 0.06); punch = s.get("punch", 0); shake = s.get("shake", 0)
    zw = s.get("zw", 1296); zh = int(zw * 1080 / 1296) // 2 * 2
    z = f"1+{push}*on/{N}+{punch}*max(0\\,1-on/18)"
    sx = f"+{shake}*sin(on*2.1)*max(0\\,1-on/24)" if shake else ""
    sy = f"+{shake}*cos(on*2.7)*max(0\\,1-on/24)" if shake else ""
    mi = ",minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:vsbmc=1" if sp < 1 else ",fps=60"
    grad = f"gradients=s=1080x1920:c0={pal[0]}:c1={pal[1]}:c2={pal[2]}:nb_colors=3:x0=0:y0=0:x1=1080:y1=600:speed=0.012:rate=60:duration={dur:.4f}"
    fade_txt = "" if s.get("nofade") else ",fade=in:st=0:d=0.18:alpha=1"
    g = (
        f"[0:v]{TM},setpts=(PTS-STARTPTS)/{sp}{mi},split=3[x][y][mm];"
        f"[mm]crop={':'.join(str(v) for v in s.get('minimap_box', COD_MINIMAP))},scale=380:-2:flags=lanczos,drawbox=x=0:y=0:w=iw:h=ih:color=white@0.55:t=3[mmap];"
        f"[x]crop=608:1080:656:0,scale=270:480,gblur=sigma=12,scale=1080:1920:flags=bicubic,eq=brightness=-0.2:saturation=0.85[bg];"
        f"[y]crop={zw}:{zh}:{s.get('cx', 312)}:{s.get('cy', 0)},scale=1296:1080:flags=lanczos,"
        f"zoompan=z='{z}':x='iw/2-iw/zoom/2{sx}':y='ih/2-ih/zoom/2{sy}':d=1:s=1080x900:fps=60"
        + (",rgbashift=rh=-14:bh=14:gv=6:enable='lt(t\\,0.15)'" if s.get("glitch") else "") + "[fg];"
        f"[bg][fg]overlay=0:470[b0];[b0][mmap]overlay=(W-w)/2:1515" + ("" if s.get("minimap", False) else ":enable=0") + "[base];"  # no lines around the sharp footage: Facebook flags framed footage as a border
        # caption masks
        f"color=black:s=1080x1920:r=60:d={dur:.4f},format=rgb24,{textlayer(s, i, dur, False)},format=gray,split=3[mo][mo2][mo3];"
        f"color=black:s=1080x1920:r=60:d={dur:.4f},format=rgb24,{textlayer(s, i, dur, True)},format=gray[mi];"
        f"{grad},format=rgba,split=3[g1][g2][g3];"
        f"[mo]gblur=sigma=22,lut=y='min(255\\,val*2.6)'[glm];[g1][glm]alphamerge{fade_txt}[glow];"
        f"[mo2]gblur=sigma=6,lut=y='min(255\\,val*1.6)'[glm2];[g3][glm2]alphamerge{fade_txt}[glow2];"
        f"color=0x0A0A14:s=1080x1920:r=60:d={dur:.4f},format=rgba[blk];[blk][mo3]alphamerge{fade_txt}[stroke];"
        f"[g2][mi]alphamerge{fade_txt}[fill];"
        f"[base][glow]overlay=0:0:shortest=1[c1];[c1][glow2]overlay[c2];[c2][stroke]overlay[c3];[c3][fill]overlay[c4];"
        # progress bar across the whole video
        f"color={pal[0]}:s=1080x10:r=60[bar];[c4][bar]overlay=x='-1080+({starts[i]:.4f}+t)/{TOT:.4f}*1080':y=0"
        + (",fade=in:st=0:d=0.15:color=white" if s.get("flash") else "")
        + (f",fade=out:st={dur - 0.5:.3f}:d=0.5" if s.get("fadeout") else "")
        + ",format=yuv420p[v];"
        f"[0:a:0]" + (f"atempo=0.5,atempo={sp / 0.5:.4f}" if sp < 0.5 else f"atempo={sp}") + f",asetpts=PTS-STARTPTS,aresample=48000,apad,atrim=0:{dur:.4f}[a]"
    )
    fc = f"{W}/fc_{i}.txt"; open(fc, "w").write(g)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-t", str(b - a), "-i", SRC, *filter_script_args(fc),
                    "-map", "[v]", "-map", "[a]", "-t", f"{dur:.4f}", "-r", "60", "-c:v", "libx264", "-preset", "slow", "-crf", "14",
                    "-profile:v", "high", "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
                    "-colorspace", "bt709", "-color_range", "tv", "-c:a", "pcm_s16le", o], check=True)
    parts.append(o); print("seg", i, round(dur, 2), flush=True)
lst = f"{W}/list.txt"; open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", OUT], check=True)
print("done", OUT, round(TOT, 2))
