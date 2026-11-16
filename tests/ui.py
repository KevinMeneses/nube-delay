"""Ayudante para probar la interfaz con cliclick (ventana del FX en su posición/tamaño por defecto)."""
import subprocess, time, pathlib, re, math
WX, WY = 26, 66 + 53            # esquina del área gráfica del FX (puntos), bajo la cabecera de REAPER
ROOT = pathlib.Path(__file__).resolve().parent.parent
def pt(x, y): return f"{round(WX + x)},{round(WY + y)}"
def cc(*args): subprocess.run(["cliclick", "-w", "60", *args], check=True); time.sleep(0.4)
def wheel(n): subprocess.run(["swift", str(ROOT / "tests/scroll.swift"), str(n)], check=True); time.sleep(0.4)
def shot(path): subprocess.run(["screencapture", "-x", "-R26,66,1000,693", path], check=True); return path
def dump():
    p = ROOT / "tests/out/dump.txt"; p.unlink(missing_ok=True)
    subprocess.Popen(["/Applications/REAPER.app/Contents/MacOS/REAPER", "-nonewinst", str(ROOT / "tests/ui_dump.lua")],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(40):
        if p.exists() and "done" in p.read_text(): return p.read_text().replace("done\n", "")
        time.sleep(0.25)
    return "(sin respuesta)"
def param(n):
    """valor formateado del slider n"""
    m = re.search(rf"^{n} (.*)$", dump(), re.M); return m.group(1).rsplit(" = ", 1)[1] if m else None
def num(s): return float(s.split()[0]) if s else float("nan")
def drag(x0, y0, x1, y1, steps=8):
    cc(f"dd:{pt(x0, y0)}")
    for k in range(1, steps + 1): cc(f"m:{pt(x0 + (x1 - x0) * k / steps, y0 + (y1 - y0) * k / steps)}")
    cc(f"du:{pt(x1, y1)}")
# layout (ventana 1000x640): dy = 54, dh = 322, py = 386
PY = 386
STYLE = lambda k: (70 + k * 96 + 46, PY + 20)
KNOB = lambda i: (56 + i * 86, PY + 92)
SMALL = lambda i: (46 + i * 72, PY + 184)
DUCK = lambda i: (436 + i * 72, PY + 184)
FREEZE, TAP, SYNC = (938, PY + 20), (846, PY + 20), (753, PY + 20)
PRESETS, ROUT, USE = (188, 22), (339, 22), (507, 22)
GRAPH = (273, 215)
FW = min(322 * 1.25, (1000 - 96 - 90) * 0.40); FX0 = 1000 - 14 - 96 - 16 - FW
f2x = lambda f: FX0 + FW * math.log(f / 20) / math.log(1000)
PT_Y = 54 + 22 + (322 - 40) * 3 / 36
