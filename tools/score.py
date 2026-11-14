"""Procedural tactical game score synced to an edit.

usage: score.py plan.json out.wav
plan: {"total": s, "bpm": 140, "sections": [[start, end, level]], "drops": [t], "risers": [t_end], "stops": [[a, b]]}
level 0 = pad only, 1 = pad+hats+light bass, 2 = full beat, 3 = full beat + lead
"""
import json, sys
import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000
rng = np.random.default_rng(11)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, "low", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, "high", fs=SR, output="sos"), x)


def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x)


def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)


def saw(f, n, detune=0.0):
    t = np.arange(n) / SR
    ph = (t * f * (1 + detune)) % 1.0
    return 2 * ph - 1


def kick(amp=1.0):
    n = int(0.45 * SR); t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t * 28)
    return amp * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)


def bass808(f, dur, amp=0.9):
    n = int(dur * SR); t = np.arange(n) / SR
    fr = f * (1 + 0.9 * np.exp(-t * 35))
    x = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 1.6) * np.minimum(1, t / 0.004)
    return amp * np.tanh(2.2 * x) / np.tanh(2.2)


def snare(amp=0.6):
    n = int(0.35 * SR); t = np.arange(n) / SR
    noise = bp(rng.standard_normal(n), 1200, 7000) * np.exp(-t * 14)
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25)
    clap = sum(np.roll(bp(rng.standard_normal(n), 900, 2500) * np.exp(-t * 60), int(k * 0.011 * SR)) for k in range(3))
    return amp * (0.55 * noise + 0.4 * body + 0.35 * clap)


def hat(amp=0.18, open_=False):
    n = int((0.22 if open_ else 0.05) * SR); t = np.arange(n) / SR
    return amp * hp(rng.standard_normal(n), 7500) * np.exp(-t * (12 if open_ else 80))


def pluck(f, amp=0.12):
    n = int(0.5 * SR); t = np.arange(n) / SR
    x = saw(f, n) + 0.5 * saw(f * 2, n, 0.003)
    return amp * lp(x * np.exp(-t * 7), 3200)


def riser(dur, amp=0.35):
    n = int(dur * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n)
    out = np.zeros(n); step = int(0.05 * SR)
    for i in range(0, n, step):  # sweeping band
        c = 400 + 7000 * (i / n) ** 2
        seg = bp(x[i:i + step + 400], c * 0.7, min(c * 1.4, 20000))[:len(out[i:i + step])]
        out[i:i + step] = seg
    tone = np.sin(2 * np.pi * np.cumsum(110 + 660 * (t / dur) ** 2) / SR) * 0.25
    return amp * (out + tone) * (t / dur) ** 2


def impact(amp=1.0):
    n = int(2.5 * SR); t = np.arange(n) / SR
    boom = np.sin(2 * np.pi * np.cumsum(35 + 80 * np.exp(-t * 12)) / SR) * np.exp(-t * 2.2)
    crash = hp(rng.standard_normal(n), 3000) * np.exp(-t * 3.5) * 0.25
    return amp * (boom + crash)


def place(buf, x, t):
    i = int(t * SR)
    if i >= len(buf) or i + len(x) <= 0:
        return
    if i < 0:
        x, i = x[-i:], 0
    j = min(len(buf), i + len(x))
    buf[i:j] += x[: j - i]


def main():
    plan = json.load(open(sys.argv[1]))
    total, bpm = plan["total"], plan.get("bpm", 140)
    n = int((total + 3) * SR)
    drums, bass, pad, lead, fx = (np.zeros(n) for _ in range(5))
    beat = 60 / bpm; bar = 4 * beat
    # D minor: i - VI - iv - V  (D, Bb, G, A); two bars each
    roots = [36.71, 29.14, 49.0, 55.0]
    chords = [[146.83, 174.61, 220.0], [116.54, 146.83, 174.61], [98.0, 116.54, 146.83], [110.0, 138.59, 164.81]]
    penta = [293.66, 349.23, 392.0, 440.0, 523.25, 587.33]

    def level(t):
        for a, b, lv in plan["sections"]:
            if a <= t < b:
                return lv
        return 0

    def stopped(t):
        return any(a <= t < b for a, b in plan.get("stops", []))

    nbars = int(total / bar) + 2
    for bi in range(nbars):
        t0 = bi * bar
        ci = (bi // 2) % 4
        # pad: whole bar, detuned saws, slow attack
        m = int(bar * SR)
        chord = sum(saw(f, m, d) for f in chords[ci] for d in (-0.004, 0.004))
        tt = np.arange(m) / SR
        penv = np.minimum(1, tt / 0.6) * np.minimum(1, (bar - tt) / 0.4)
        place(pad, lp(chord, 900) * penv * 0.05, t0)
        for s in range(16):  # 16ths
            t = t0 + s * beat / 4
            if t >= total:
                break
            lv = level(t)
            if stopped(t):
                continue
            # hats
            if lv >= 1 and s % 2 == 0:
                place(drums, hat(0.16 if s % 4 else 0.2), t)
            if lv >= 2 and s % 2 == 1 and rng.random() < 0.35:
                place(drums, hat(0.1), t)
            if lv >= 2 and s in (14, 15) and bi % 2 == 1:  # roll into next bar
                for r in range(3):
                    place(drums, hat(0.12), t + r * beat / 12)
            if lv >= 2 and s == 6 and bi % 4 == 3:
                place(drums, hat(0.12, True), t)
            # half-time: kick on 1 and the "and" of 2, snare on 3
            if lv >= 2 and s in (0, 6, 10):
                place(drums, kick(0.9 if s == 0 else 0.7), t)
            if lv >= 2 and s == 8:
                place(drums, snare(0.55), t)
            # 808 on 1 (and pickup) — light from level 1
            if lv >= 1 and s in (0, 10):
                place(bass, bass808(roots[ci] * (2 if s == 10 and ci == 3 else 1), beat * (2.4 if s == 0 else 1.4), 0.75 if lv >= 2 else 0.45), t)
            # lead arp
            if lv >= 3 and s % 3 == 0:
                f = penta[(s // 3 + bi) % len(penta)]
                place(lead, pluck(f, 0.08), t)
    for t in plan.get("risers", []):
        d = 2.0
        place(fx, riser(d, 0.3), t - d)
    for t in plan.get("drops", []):
        place(fx, impact(0.9), t)
    # bus processing
    drums = np.tanh(1.4 * drums) / np.tanh(1.4)
    bass = lp(bass, 220)
    mix = 0.9 * drums + 0.9 * bass + pad + lead + fx
    # stereo: pad and lead slightly wide
    l = mix + 0.15 * np.roll(pad + lead, 300)
    r = mix + 0.15 * np.roll(pad + lead, -300)
    st = np.stack([l, r], 1)[: int(total * SR)]
    fade = int(1.5 * SR); st[-fade:] *= np.linspace(1, 0, fade)[:, None]
    st /= np.max(np.abs(st)) / 0.89
    import soundfile as sf
    sf.write(sys.argv[2], st.astype(np.float32), SR, subtype="PCM_24")
    print("wrote", sys.argv[2], round(total, 2), "s")


main()
