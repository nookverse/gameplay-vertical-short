"""Glowing-style 1080x1920 cover/thumbnail from a JSON spec.

usage: python3 cover_glow.py spec.json
spec = {
  "out": "/abs/thumbnails/shorts-reels-thumbnail.jpg",
  "bg":  {"img": "/abs/h_1205.png", "x": 600},              # 608x1080 slice at x, scaled to 1080x1920, darkened
  "glow": {"color": "0xFFB000", "x": -60, "y": 330},        # optional soft colour glow behind the main card
  "cards": [                                                 # UI cards cropped from tone-mapped full-res frames
     {"img": "/abs/h_1170.8.png", "crop": [285,305,537,207], "w": 600, "x": 40, "y": 470, "rot": -0.05, "border": "0xFFD27A"}
  ],
  "circle": {"img": "/abs/h_1220.png", "crop": [420,420,750,390], "d": 330, "x": 715, "y": 1015, "ring": "0x39FF14"},  # optional
  "texts": [                                                 # glowing gradient text, centred unless xoff
     {"text": "NEW SNIPER", "size": 196, "y": 30, "pal": "ultra", "bw": 12},
     {"text": "ASTAROTH .57 MANUAL", "size": 96, "y": 300, "pal": "neon", "bw": 8}
  ],
  "strip": true                                              # neon gradient strip at the bottom
}
Palettes: neon, toxic, sunset, ultra, ice, violet, gold. Keep every text inside 1080 px (shrink size if it clips).
Frames: grab them with grab.py (tone-mapped, full resolution) before cropping.
"""
import json, subprocess, sys, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gvs import filter_script_args, font

F = font()
PAL = {"neon": ("0x00F0FF", "0xFF2BD6", "0x7A5CFF"), "toxic": ("0x39FF14", "0x00F0FF", "0xB6FF00"),
       "sunset": ("0xFF7A00", "0xFF2B8A", "0xFFD400"), "ultra": ("0xFF1E3C", "0xFFB000", "0xFF5A00"),
       "ice": ("0x7DF9FF", "0xFFFFFF", "0x3D7BFF"), "violet": ("0xB04BFF", "0x00E5FF", "0xFF4BD8"),
       "gold": ("0xFFD400", "0xFF7A00", "0xFFB000")}
spec = json.load(open(sys.argv[1]))
tmp = tempfile.mkdtemp(prefix="cover_")
ins = []
def inp(path):
    ins.append(path); return f"[{len(ins) - 1}]"

def glow(n, t):
    p = f"{tmp}/{n}.txt"; open(p, "w").write(t["text"])
    c0, c1, c2 = PAL[t.get("pal", "neon")]; y = t["y"]; sz = t["size"]; bw = t.get("bw", 10); xo = t.get("xoff", 0)
    dt = f"drawtext=fontfile={F}:textfile={p}:fontsize={sz}:fontcolor=white"
    return (f"color=black:s=1080x1920,format=rgb24,{dt}:borderw={bw}:bordercolor=white:x=(w-text_w)/2+{xo}:y={y},format=gray,split=3[{n}o][{n}o2][{n}o3];"
            f"color=black:s=1080x1920,format=rgb24,{dt}:x=(w-text_w)/2+{xo}:y={y},format=gray[{n}i];"
            f"gradients=s=1080x1920:c0={c0}:c1={c1}:c2={c2}:nb_colors=3:x0=0:y0={y}:x1=1080:y1={y + 400}:d=1,format=rgba,split=3[{n}g1][{n}g2][{n}g3];"
            f"[{n}o]gblur=sigma=26,lut=y='min(255\\,val*2.8)'[{n}gm];[{n}g1][{n}gm]alphamerge[{n}gl];"
            f"[{n}o2]gblur=sigma=7,lut=y='min(255\\,val*1.6)'[{n}gm2];[{n}g3][{n}gm2]alphamerge[{n}gl2];"
            f"color=0x0A0A14:s=1080x1920,format=rgba[{n}bk];[{n}bk][{n}o3]alphamerge[{n}st];[{n}g2][{n}i]alphamerge[{n}fi];")

b = spec["bg"]
s = (f"{inp(b['img'])}crop=608:1080:{b.get('x', 656)}:0,scale=1080:1920:flags=lanczos,gblur=sigma=5,eq=brightness=-0.22:saturation=1.1,format=rgba[bg];"
     "color=black:s=1080x1920,format=rgba,geq=r=0:g=0:b=0:a='if(lt(Y\\,560)\\,230*(1-Y/700)\\,if(gt(Y\\,1380)\\,245*min(1\\,(Y-1380)/260)\\,0))'[grad];[bg][grad]overlay[L0];")
last = "L0"; k = 0
def ov(label, x, y):
    global last, k
    k += 1; nl = f"L{k}"
    out = f"[{last}][{label}]overlay={x}:{y}[{nl}];"; last = nl; return out
if spec.get("glow"):
    g = spec["glow"]
    s += f"color={g['color']}:s=520x820,format=rgba,pad=920:1220:200:200:color={g['color']}@0,gblur=sigma=55[gw];" + ov("gw", g["x"], g["y"])
for i, c in enumerate(spec.get("cards", [])):
    w, h, x, y = c["crop"]; r = c.get("rot", 0)
    s += (f"{inp(c['img'])}crop={w}:{h}:{x}:{y},scale={c['w']}:-1:flags=lanczos,pad=iw+16:ih+16:8:8:color={c.get('border', '0xFFFFFF')},"
          f"format=rgba,rotate=a={r}:ow=rotw({r}):oh=roth({r}):c=none[card{i}];") + ov(f"card{i}", c["x"], c["y"])
if spec.get("circle"):
    c = spec["circle"]; w, h, x, y = c["crop"]; d = c["d"]; R = d // 2; rc = c.get("ring", "0xFFFFFF")
    s += (f"{inp(c['img'])}crop={w}:{h}:{x}:{y},scale={d}:{d}:flags=lanczos,format=rgba,geq=r='r(X\\,Y)':g='g(X\\,Y)':b='b(X\\,Y)':a='if(lt(hypot(X-{R}\\,Y-{R})\\,{R - 5})\\,255\\,0)'[circ];"
          f"color=white@0:s={d + 30}x{d + 30},format=rgba,geq=r={int(rc[2:4], 16)}:g={int(rc[4:6], 16)}:b={int(rc[6:8], 16)}:a='if(between(hypot(X-{R + 15}\\,Y-{R + 15})\\,{R - 7}\\,{R + 9})\\,255\\,0)'[ring];")
    s += ov("ring", c["x"] - 15, c["y"] - 15) + ov("circ", c["x"], c["y"])
for i, t in enumerate(spec.get("texts", [])):
    n = f"T{i}"; s += glow(n, t)
    for lay in ("gl", "gl2", "st", "fi"):
        s += ov(f"{n}{lay}", 0, 0)
if spec.get("strip", True):
    s += "gradients=s=1080x70:c0=0xFFB000:c1=0xFF2BD6:c2=0x00F0FF:nb_colors=3:x0=0:y0=0:x1=1080:y1=0:d=1,format=rgba[strip];" + ov("strip", 0, 1850)
s += f"[{last}]format=yuvj420p[out]"
fc = f"{tmp}/cover.fc"; open(fc, "w").write(s)
args = []
for p in ins: args += ["-i", p]
subprocess.run(["ffmpeg", "-v", "error", "-y", *args, *filter_script_args(fc), "-map", "[out]", "-frames:v", "1", "-q:v", "2", spec["out"]], check=True)
print("cover ->", spec["out"])
