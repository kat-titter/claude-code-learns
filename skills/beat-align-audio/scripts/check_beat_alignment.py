#!/usr/bin/env python3
"""Check whether two audio excerpts are beat-aligned when overlapped.
Usage: check_beat_alignment.py A.wav B.wav --bpm 124 [--out-start S] [--in-start S] [--seconds 16] [--png out.png]
Takes A from --out-start and B from --in-start (seconds), overlays them, and reports:
  local kick phase of each (ms vs a beat grid starting at the excerpt start),
  the waveform-match lag (ms) that best aligns B to A (+-2 beats), and its score.
Writes a stacked-waveform PNG with beat lines for visual confirmation."""
import argparse
import sys
if sys.argv[1:2] in (['-h'], ['--help']):
    print(__doc__); sys.exit(0)
try:
    import numpy as np, soundfile as sf, librosa
    from scipy import signal
except ImportError as e:
    raise SystemExit(f'{e.name} missing: pip install numpy soundfile librosa scipy matplotlib (or run with the project venv that has them)')

ap = argparse.ArgumentParser()
ap.add_argument("a"); ap.add_argument("b"); ap.add_argument("--bpm", type=float, required=True)
ap.add_argument("--out-start", type=float, default=0); ap.add_argument("--in-start", type=float, default=0)
ap.add_argument("--seconds", type=float, default=16); ap.add_argument("--png", default="alignment.png")
g = ap.parse_args()


def load(p, t0, dur):
    x, sr = sf.read(p, always_2d=True, dtype="float32")
    x = x.mean(1)
    if sr != 44100:
        x = librosa.resample(x, orig_sr=sr, target_sr=44100)
    return x[int(t0 * 44100):int((t0 + dur) * 44100)]


SR = 44100
A, B = load(g.a, g.out_start, g.seconds), load(g.b, g.in_start, g.seconds)
n = min(len(A), len(B)); A, B = A[:n], B[:n]
beat = 60 / g.bpm
kick = signal.butter(4, 150, "low", fs=SR, output="sos")


def phase(x):
    env = signal.sosfiltfilt(signal.butter(2, 40, "low", fs=SR, output="sos"), np.abs(signal.hilbert(signal.sosfiltfilt(kick, x))))
    ph = ((np.arange(len(env)) / SR) / beat) % 1.0
    idx = np.minimum((ph * 64).astype(int), 63)
    fold = np.bincount(idx, weights=env, minlength=64) / (np.bincount(idx, minlength=64) + 1e-9)
    s = (np.argmax(fold) + 0.5) / 64 - 0.012 / beat
    return (s - 1 if s > 0.5 else s) * beat * 1000, fold.max() / (fold.mean() + 1e-12)


def lag(a, b):
    hop = 64
    ea = librosa.onset.onset_strength(y=a, sr=SR, hop_length=hop); eb = librosa.onset.onset_strength(y=b, sr=SR, hop_length=hop)
    ea, eb = (ea - ea.mean()) / (ea.std() + 1e-9), (eb - eb.mean()) / (eb.std() + 1e-9)
    m = int(2 * beat * SR / hop); ls = np.arange(-m, m + 1)
    cc = np.array([np.dot(ea[max(l, 0):len(ea) + min(l, 0)], eb[max(-l, 0):len(eb) - max(l, 0)]) / (len(ea) - abs(l)) for l in ls])
    ok = np.where(cc >= cc.max() * 0.97)[0]; i = ok[np.argmin(np.abs(ls[ok]))]
    return ls[i] * hop / SR * 1000, cc.max()


pa, ca = phase(A); pb, cb = phase(B); lg, sc = lag(A, B)
print(f"A kick phase {pa:+.0f} ms (contrast {ca:.2f}); B kick phase {pb:+.0f} ms (contrast {cb:.2f})")
print(f"waveform match: move B by {lg:+.1f} ms (score {sc:.2f}); |lag| < 15 ms = locked; > {beat*500:.0f} ms = bar-phase issue")
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
w = int(8 * beat * SR); t = np.arange(min(w, n)) / SR
fig, ax = plt.subplots(2, 1, figsize=(14, 3.6), sharex=True)
for r, (x, c, nm) in enumerate(((A, "#e0583a", "A"), (B, "#3a8ee0", "B"))):
    ax[r].plot(t, x[:len(t)], color=c, lw=0.5)
    for k in range(9): ax[r].axvline(k * beat, color="k", lw=0.6, alpha=1 if k % 4 == 0 else 0.4)
    ax[r].set_yticks([]); ax[r].set_ylabel(nm)
ax[1].set_xlabel("seconds (2 bars, beat lines)"); fig.tight_layout(); fig.savefig(g.png)
print("wrote", g.png)
