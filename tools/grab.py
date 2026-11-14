"""One frame (tone-mapped if HDR) with an optional time stamp, or a contact sheet of many.

usage: python3 grab.py <src> <t> <out.png> [width]            one frame (width 0 = full resolution, no stamp)
       python3 grab.py --sheet <src> <start> <len> <fps> <out.jpg> [cols=6]   contact sheet, time-stamped
"""
import os, subprocess, sys
from gvs import die, font, tonemap

a = sys.argv[1:]
if a[:1] == ["--sheet"] and len(a) >= 6:
    src, start, length, fps, out = a[1:6]; cols = int(a[6]) if len(a) > 6 else 6
    n = max(1, round(float(length) * float(fps))); rows = -(-n // cols)
    vf = (f"fps={fps},{tonemap(src)},scale=400:-2,drawtext=fontfile={font()}:text='%{{pts\\:flt}}':"
          f"fontsize=26:fontcolor=yellow:borderw=3:x=4:y=4,tile={cols}x{rows}")
    # setpts keeps the stamp in source time
    vf = f"setpts=PTS+{float(start)}/TB," + vf
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", start, "-t", length, "-i", src, "-vf", vf,
                    "-frames:v", "1", out], check=True)
elif len(a) in (3, 4):
    src, t, out = a[:3]; w = int(a[3]) if len(a) == 4 else 480
    if not os.path.isfile(src):
        die(f"source not found: {src}")
    vf = tonemap(src)
    if w:
        vf += f",scale={w}:-2,drawtext=fontfile={font()}:text='{t}':fontsize=34:fontcolor=yellow:borderw=3:x=6:y=4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", t, "-i", src, "-frames:v", "1", "-vf", vf, out], check=True)
else:
    die(__doc__.strip().splitlines()[2].strip())
print(out)
