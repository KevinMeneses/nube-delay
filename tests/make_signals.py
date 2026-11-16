"""Señales de prueba (48 kHz, float32)."""
import numpy as np, soundfile as sf, pathlib, shutil
D = pathlib.Path(__file__).parent / "signals"; D.mkdir(exist_ok=True)
SR = 48000
def a(db): return 10 ** (db / 20)
def save(name, *ch): sf.write(D / name, np.stack(ch, 1).astype(np.float32), SR, subtype="FLOAT")
n = SR * 3; t = np.arange(n) / SR
imp = np.zeros(n); imp[int(0.1 * SR)] = 0.5
save("impulse.wav", imp, imp); save("impulseL.wav", imp, np.zeros(n))
s = lambda f, db: a(db) * np.sin(2 * np.pi * f * t)
save("s100.wav", s(100, -12), s(100, -12)); save("s8k.wav", s(8000, -12), s(8000, -12))
save("s1k_m6.wav", s(1000, -6), s(1000, -6))
save("lr.wav", s(1000, -12), s(1500, -12))
t4 = np.arange(SR * 4) / SR; d = np.where(t4 < 1.5, a(-10) * np.sin(2 * np.pi * 1000 * t4), 0); save("duck.wav", d, d)
v = pathlib.Path.home() / "Music/NubeDeEss/tests/signals/voz.wav"
if v.exists(): shutil.copy(v, D / "voz.wav")
print("ok", sorted(p.name for p in D.iterdir()))
