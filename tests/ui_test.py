"""Pruebas de la interfaz con el mouse. Requiere la demo abierta (tests/reopen.sh) y la ventana del FX al frente."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from ui import *
OUT = os.environ.get("NUBE_SHOTS", str(ROOT / "tests/out"))
fails = 0
def check(name, got, want):
    global fails
    ok = (want(got) if callable(want) else got == want); fails += not ok
    print(f"{'OK ' if ok else 'MAL'} {name:44s} {got!r}")

subprocess.run(["osascript", "-e", 'tell application "REAPER" to activate']); time.sleep(0.6)
cc(f"c:{pt(500, 5)}")
check("arranca con preset 2 (ping-pong, 1/8.)", (param(6), param(2)), ("Ping-pong", "1/8."))
cc(f"c:{pt(*STYLE(1))}"); check("clic en Cinta", param(7), "Cinta")
cc(f"c:{pt(*SYNC)}"); check("A tempo apagado", param(2), "Apagado")
x, y = KNOB(0); t0 = num(param(1)); drag(x, y, x, y - 40)
check("arrastrar Tiempo (ms) sube", num(param(1)), lambda v: v > t0 * 1.3)
cc(f"dc:{pt(x, y)}"); check("doble clic en Tiempo = 375 ms", num(param(1)), 375.0)
cc(f"c:{pt(*SYNC)}"); check("A tempo vuelve a 1/8.", param(2), "1/8.")
cc(f"m:{pt(x, y)}"); wheel(1); check("rueda sobre Tiempo: una figura mas", param(2), "1/4")
f0 = num(param(4)); drag(*GRAPH, GRAPH[0], GRAPH[1] - 50)
check("arrastrar en los ecos sube el feedback", num(param(4)), lambda v: v > f0 + 10)
x = f2x(num(param(8))); drag(x, PT_Y, x + 40, PT_Y)
check("arrastrar el punto grave a la derecha", num(param(8)), lambda v: v > 450)
x, y = DUCK(0); drag(x, y, x, y - 30); check("arrastrar Ducking sube", num(param(15)), lambda v: v > 11)
for _ in range(4): subprocess.run(["cliclick", f"c:{pt(*TAP)}"]); time.sleep(0.5)
time.sleep(0.3); check("Tap x4 cada ~0.5 s -> ~500 ms", (param(2), num(param(1))), lambda v: v[0] == "Apagado" and 420 < v[1] < 640)
cc(f"c:{pt(*FREEZE)}"); check("Freeze encendido", param(18), "Encendido")
time.sleep(1.0); shot(f"{OUT}/ui_delay_freeze.png")
cc(f"c:{pt(*FREEZE)}"); check("Freeze apagado", param(18), "Apagado")
cc(f"c:{pt(*USE)}"); check("Uso envio", param(19), lambda v: v.startswith("Envio"))
cc(f"c:{pt(*USE)}"); check("Uso inserto", param(19), "Inserto")
cc(f"c:{pt(*ROUT)}"); time.sleep(0.6); cc("kp:arrow-down", "kp:arrow-down", "kp:arrow-down", "kp:return")
check("menu Ruteo -> Mono", param(6), "Mono")
cc(f"c:{pt(*PRESETS)}"); time.sleep(0.6); cc("kp:arrow-down", "kp:return")
check("menu Presets -> Voz negra con ducking", (param(7), num(param(15)), param(2)), ("Cinta", 8.0, "1/4"))
print("FALLAS:", fails)
sys.exit(1 if fails else 0)
