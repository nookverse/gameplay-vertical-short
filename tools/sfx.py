"""Place sound effects on the timeline.

usage: python3 sfx.py sfx.json <total_seconds> out.wav
sfx.json: [[time, "key or /absolute/file.wav", length_s, gain_dB], ...]   ([] = silent track)
Keys are looked up in GVS_SFX_DIR. The built-in key names match files in Blackmagic Design's free
Fairlight Sound Library (a separate free download; use its "Media Files" folder). Point GVS_SFX_DIR
there, or use your own files by absolute path or by file name inside GVS_SFX_DIR.
"""
import sys, json, subprocess, os
L=os.path.expanduser(os.environ.get("GVS_SFX_DIR",""))
F={"impact":"Metal Pipe Impacts Good.M.wav","whoosh":"Whooshes Quick Succession, Twirling Fast.M.wav","lowwhoosh":"Low Whoosh x2.wav",
"cardoor":"Car Door Shut.M.wav","jeep":"Jeep Metal Rattle Suspension.M.wav","keys":"Keys Rattle.M.wav","keyslight":"Keys Movement.M.wav",
"lock":"Key in Lock.M.wav","latch":"Metal Door Latch Movement.M.wav","locker":"Metal Locker Open 1.M.wav","hiss":"Shower On Run Off.M.wav",
"zip":"Quick Bag Load Zipper Close.M.wav","rummage":"Backpack Bookbag Rummage.M.wav","cock":"Gun Load Cock Click.M.wav",
"gear":"Soldier Metal Gear Movement, Rattles.wav","catwalk":"FS catwalk on metal tinny.M.wav","toolbox":"Metal Box Banging.M.wav","map":"Map Handle 1.M.wav"}
ev=json.load(open(sys.argv[1])); total=float(sys.argv[2]); out=sys.argv[3]
if not ev:
    subprocess.run(["ffmpeg","-v","error","-y","-f","lavfi","-i","anullsrc=r=48000:cl=stereo","-t",str(total),out],check=True)
    print("no events; wrote silent",out); sys.exit(0)
def resolve(k):
    for p in ([os.path.join(L,F[k])] if k in F and L else [])+[k]+([os.path.join(L,k)] if L else []):
        if os.path.isfile(p): return p
    sys.exit(f"error: sound effect {k!r} not found" + ("" if L else " (set GVS_SFX_DIR to your sound folder)"))
args=[]; fc=[]
for n,(t,k,ln,g) in enumerate(ev):
    args+=["-i",resolve(k)]
    fo=min(0.25,ln/3)
    fc.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,silenceremove=start_periods=1:start_threshold=-45dB,atrim=0:{ln},asetpts=N/SR/TB,afade=t=in:d=0.02,afade=t=out:st={ln-fo}:d={fo},volume={g}dB,adelay={int(t*1000)}|{int(t*1000)}[s{n}]")
fc.append("".join(f"[s{n}]" for n in range(len(ev)))+f"amix=inputs={len(ev)}:normalize=0:duration=longest,apad=whole_dur={total},atrim=0:{total}[out]")
subprocess.run(["ffmpeg","-v","error","-y",*args,"-filter_complex",";".join(fc),"-map","[out]","-ar","48000",out],check=True)
print("ok",len(ev),"events ->",out)
