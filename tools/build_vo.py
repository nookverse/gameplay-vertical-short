"""Place each vo/l{n}.wav at the start of its segment -> vo.wav, and write times.json (segment starts).

usage: python3 build_vo.py <workdir>     (segments without "vo" get none; no voiceover at all -> silent vo.wav)
"""
import json,subprocess,sys
W=sys.argv[1]; segs=json.load(open(f"{W}/segs.json"))
d=[(s["out"]-s["in"])/s["speed"] for s in segs]; st=[sum(d[:i]) for i in range(len(d))]; tot=sum(d)
json.dump({"starts":st,"total":tot},open(f"{W}/times.json","w"))
# VO
ins=[];fc=[]
n=0
for i,s in enumerate(segs):
    if "vo" not in s: continue
    t=st[i]+(0.1 if i==0 else 0.2)
    ins+=["-i",f"{W}/vo/l{s['vo']}.wav"]; fc.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={int(t*1000)}|{int(t*1000)}[v{n}]"); n+=1
if n==0:  # no voiceover: a silent track keeps mix.sh unchanged
    subprocess.run(["ffmpeg","-v","error","-y","-f","lavfi","-i",f"anullsrc=r=48000:cl=stereo","-t",f"{tot:.4f}",f"{W}/vo.wav"],check=True)
    print("no voiceover lines; wrote silent vo.wav, total",round(tot,2)); sys.exit(0)
fc.append("".join(f"[v{i}]" for i in range(n))+f"amix=inputs={n}:normalize=0,apad=whole_dur={tot},atrim=0:{tot},highpass=f=80,equalizer=f=3500:t=q:w=1:g=2,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,volume=3dB[o]")
subprocess.run(["ffmpeg","-v","error","-y",*ins,"-filter_complex",";".join(fc),"-map","[o]","-ar","48000",f"{W}/vo.wav"],check=True)
print("total",round(tot,2),"starts",[round(x,2) for x in st])
