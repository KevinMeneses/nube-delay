"""Compara los renders de tests/out con lo que dice la teoría. Sale con código 1 si algo falla."""
import numpy as np, soundfile as sf, pathlib, sys
from scipy import signal as sg
D = pathlib.Path(__file__).parent / "out"; S = pathlib.Path(__file__).parent / "signals"; SR = 48000
def a(db): return 10 ** (db / 20)
def db(x): return 20 * np.log10(np.abs(x) + 1e-15)
def load(name):
    x, sr = sf.read(D / f"{name}.wav"); assert sr == SR; return x
def tone(x, f, t0, t1):
    seg = x[int(t0 * SR):int(t1 * SR)]; tt = np.arange(int(t0 * SR), int(t1 * SR)) / SR
    M = np.stack([np.sin(2 * np.pi * f * tt), np.cos(2 * np.pi * f * tt)], 1)
    c, *_ = np.linalg.lstsq(M, seg, rcond=None); return db(np.hypot(*c))
T0 = int(0.1 * SR)
def echo(x, t_ms, win=0.002):
    """(posición en muestras, nivel dB) del pico cerca de t_ms después del impulso"""
    c = T0 + int(round(t_ms * SR / 1000)); w = int(win * SR); seg = np.abs(x[c - w:c + w]); i = seg.argmax()
    return c - w + i - T0, db(seg[i] / 0.5)

fails = 0
def scalar(name, got, want, tol):
    global fails
    ok = abs(got - want) <= tol; fails += not ok
    print(f"{'OK ' if ok else 'MAL'} {name:40s} {got:+9.2f}   (esperado {want:+.2f} ± {tol})")
def inrange(name, got, lo, hi):
    global fails
    ok = lo <= got <= hi; fails += not ok
    print(f"{'OK ' if ok else 'MAL'} {name:40s} {got:+9.2f}   (entre {lo:+.2f} y {hi:+.2f})")

for p in sorted(q for q in D.glob("*.wav") if not q.stem.startswith("perf_")):
    x = load(p.stem)
    if not np.all(np.isfinite(x)) or np.abs(x).max() > 2:
        fails += 1; print("MAL", p.stem, "tiene NaN o pasa de +6 dBFS")

x = load("echo")[:, 0]
p1, l1 = echo(x, 250); p2, l2 = echo(x, 500); p3, l3 = echo(x, 750)
scalar("eco 1 en 250 ms (muestras)", p1, 12000, 0)
scalar("eco 2 en 500 ms (muestras)", p2, 24000, 0)
scalar("eco 1 a 0 dB (envio)", l1, 0, 0.05)
scalar("feedback 50 %: eco 2 / eco 1", l2 - l1, db(0.5), 0.05)
scalar("feedback 50 %: eco 3 / eco 2", l3 - l2, db(0.5), 0.05)
inrange("antes del eco: silencio", db(np.abs(x[T0 + 10:T0 + 11900]).max()), -300, -90)
scalar("a tempo 1/4 a 120 BPM = 500 ms", echo(load("sync_q")[:, 0], 500)[0], 24000, 0)
scalar("a tempo 1/8 con puntillo = 375 ms", echo(load("sync_dot8")[:, 0], 375)[0], 18000, 0)
x = load("pingpong")
scalar("ping-pong: eco 1 a la izq. (suma / 2)", echo(x[:, 0], 250)[1], db(0.5), 0.05)
inrange("ping-pong: eco 1 nada a la derecha", echo(x[:, 1], 250)[1], -300, -80)
scalar("ping-pong: eco 2 a la derecha", echo(x[:, 1], 500)[1], db(0.25), 0.05)
inrange("ping-pong: eco 2 nada a la izquierda", echo(x[:, 0], 500)[1], -300, -80)
scalar("ping-pong: eco 3 a la izquierda", echo(x[:, 0], 750)[1], db(0.125), 0.05)
x = load("desfase")
scalar("desfase R +20 %: eco R en 300 ms", echo(x[:, 1], 300)[0], 14400, 0)
scalar("desfase R +20 %: eco L en 250 ms", echo(x[:, 0], 250)[0], 12000, 0)
x = load("mono")
scalar("mono: eco L = suma / 2", echo(x[:, 0], 250)[1], db(0.5), 0.05)
scalar("mono: eco R = eco L", echo(x[:, 1], 250)[1], db(0.5), 0.05)
x = load("fb0")[:, 0]
inrange("feedback 0: no hay eco 2", echo(x, 500)[1], -300, -80)
x = load("fb100")[:, 0]
scalar("feedback 100 %: eco 10 = eco 1", echo(x, 2000)[1] - echo(x, 200)[1], 0, 0.2)
ins, _ = sf.read(S / "impulse.wav")
inrange("mezcla 0 %: = entrada (nulo)", db(np.abs(load("mix0") - ins).max()), -300, -100)
x = load("mix50")[:, 0]
scalar("mezcla 50 %: seca -3 dB (sin latencia)", db(x[T0] / 0.5), db(np.cos(np.pi / 4)), 0.05)
scalar("mezcla 50 %: eco -3 dB", echo(x, 250)[1], db(np.sin(np.pi / 4)), 0.05)

def w4(f, fc): return np.tan(np.pi * f / SR) / np.tan(np.pi * fc / SR)
scalar("corte grave 400 Hz (100 Hz)", tone(load("hp400")[:, 0], 100, 1.0, 2.5), -12 + db(1 / np.sqrt(1 + w4(400, 100) ** 4)), 0.15)
scalar("corte agudo 2 kHz (8 kHz)", tone(load("lp2k")[:, 0], 8000, 1.0, 2.5), -12 + db(1 / np.sqrt(1 + w4(8000, 2000) ** 4)), 0.15)

xd, xn = load("duck")[:, 0], load("noduck")[:, 0]
def rms(x, t0, t1): return db(np.sqrt(np.mean(x[int(t0 * SR):int(t1 * SR)] ** 2)))
scalar("ducking: el eco baja 12 dB con voz", rms(xd, 0.7, 1.4) - rms(xn, 0.7, 1.4), -12, 0.5)
inrange("ducking: vuelve en el silencio", rms(xd, 2.4, 3.4) - rms(xn, 2.4, 3.4), -1.0, 0.1)
x = load("width0")
inrange("ancho 0 %: eco mono (L = R)", db(np.abs(x[SR:, 0] - x[SR:, 1]).max()), -300, -90)

def harm(x, k):
    seg = x[SR:SR + 32768] * np.hanning(32768); X = np.abs(np.fft.rfft(seg)); f = np.fft.rfftfreq(32768, 1 / SR)
    pk = lambda fr: X[(f > fr - 30) & (f < fr + 30)].max(); return db(pk(1000 * k) / pk(1000))
inrange("saturacion 0 %: sin armonicos", harm(load("sat0")[:, 0], 3), -300, -90)
inrange("saturacion 100 %: armonicos (H3)", harm(load("sat100")[:, 0], 3), -40, -10)
def spread(x):
    seg = x[SR:SR + 65536] * np.hanning(65536); X = np.abs(np.fft.rfft(seg)) ** 2; f = np.fft.rfftfreq(65536, 1 / SR)
    return 10 * np.log10(X[(np.abs(f - 1000) > 3) & (np.abs(f - 1000) < 200)].sum() / X[np.abs(f - 1000) <= 3].sum())
s0, s1 = spread(load("sat0")[:, 0]), spread(load("mod100")[:, 0])
print(f"    energia fuera de 1 kHz (±3..200 Hz): sin mod {s0:.1f} dB, mod 100 % {s1:.1f} dB")
inrange("modulacion: el eco se mueve (wow)", s1 - s0, 20, 200)
xe, xd2 = load("fb0")[:, 0], load("dif100")[:, 0]
pe, pd = echo(xe, 250)[1], db(np.abs(xd2[T0 + 11000:T0 + 20000]).max() / 0.5)
ee = 10 * np.log10(np.sum(xe[T0 + 11000:T0 + 30000] ** 2)); ed = 10 * np.log10(np.sum(xd2[T0 + 11000:T0 + 30000] ** 2))
print(f"    difusion: pico {pe:.1f} -> {pd:.1f} dB, energia {ee:.1f} -> {ed:.1f} dB")
inrange("difusion: el eco se desenfoca (pico)", pe - pd, 6, 40)
scalar("difusion: misma energia", ed - ee, 0, 3)
inrange("freeze: no graba lo que entra", db(np.abs(load("freeze")).max()), -300, -90)
scalar("salida -6", echo(load("salida")[:, 0], 250)[1], -6, 0.05)
for st in range(5):
    x = load(f"style{st}")[:, 0]
    p, l = echo(x, 250, 0.006); _, l5 = echo(x, 1250, 0.012)
    inrange(f"estilo {st}: eco 1 cerca de 250 ms (ms)", (p - 12000) / 48, -0.5 if st == 0 else -6, 0.5 if st == 0 else 6)
    inrange(f"estilo {st}: se apaga (eco 5 < eco 1)", l5 - l, -300 if st == 3 else -80, -10)
v = load("voz_seca")
for p in range(1, 12):
    x = load(f"preset{p}"); dif = x - v
    inrange(f"preset {p}: hay eco (dB bajo la voz)", db(np.sqrt(np.mean(dif ** 2)) / np.sqrt(np.mean(v ** 2))), -40, 6)
print("\nFALLAS:", fails)
sys.exit(1 if fails else 0)
