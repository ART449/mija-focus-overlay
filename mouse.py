"""
M.I.J.A Mouse Driver
─────────────────────
Simula clicks reales del sistema operativo a partir de coordenadas de pixel.
Lo usa el API cuando el usuario dice "haz click en B3" o "arrastra de A1 a F7".

Como el overlay es click-through (WS_EX_TRANSPARENT), mover el cursor sobre
él y disparar el click pasa el evento limpio a la app de abajo — exactamente
lo que queremos para accesibilidad motriz.
"""

import time

import win32api
import win32con


def _btn_codes(button: str):
    button = button.lower()
    if button in ("left", "izquierdo", "izq"):
        return win32con.MOUSEEVENTF_LEFTDOWN, win32con.MOUSEEVENTF_LEFTUP
    if button in ("right", "derecho", "der"):
        return win32con.MOUSEEVENTF_RIGHTDOWN, win32con.MOUSEEVENTF_RIGHTUP
    if button in ("middle", "medio", "centro"):
        return win32con.MOUSEEVENTF_MIDDLEDOWN, win32con.MOUSEEVENTF_MIDDLEUP
    raise ValueError(f"Botón desconocido: {button!r}")


def move(x: int, y: int):
    """Mueve el cursor a (x, y) absolutos sin hacer click."""
    win32api.SetCursorPos((x, y))


def click(x: int, y: int, button: str = "left", double: bool = False):
    """Click en (x, y). Si double=True hace doble click."""
    down, up = _btn_codes(button)
    win32api.SetCursorPos((x, y))
    time.sleep(0.05)

    presses = 2 if double else 1
    for i in range(presses):
        win32api.mouse_event(down, 0, 0, 0, 0)
        time.sleep(0.03)
        win32api.mouse_event(up, 0, 0, 0, 0)
        if i < presses - 1:
            time.sleep(0.06)


def drag(x1: int, y1: int, x2: int, y2: int, duration: float = 0.45):
    """Arrastra el cursor desde (x1,y1) hasta (x2,y2) con movimiento suavizado.
    Útil para 'desliza de B3 a F7' o seleccionar texto / mover ventanas."""
    win32api.SetCursorPos((x1, y1))
    time.sleep(0.08)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)

    steps = max(24, int(duration * 60))
    for i in range(1, steps + 1):
        t = i / steps
        eased = 3 * t * t - 2 * t * t * t   # smoothstep
        x = int(x1 + (x2 - x1) * eased)
        y = int(y1 + (y2 - y1) * eased)
        win32api.SetCursorPos((x, y))
        time.sleep(duration / steps)

    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


def scroll(x: int, y: int, direction: str = "up", clicks: int = 3):
    """Scroll en la posición indicada. Cada 'click' = 1 notch del scroll del mouse."""
    win32api.SetCursorPos((x, y))
    time.sleep(0.05)
    sign = 1 if direction.lower() in ("up", "arriba", "subir") else -1
    for _ in range(max(1, clicks)):
        win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, 120 * sign, 0)
        time.sleep(0.05)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("Usage:")
        print("  python mouse.py click <x> <y> [left|right|middle] [single|double]")
        print("  python mouse.py drag  <x1> <y1> <x2> <y2> [duration_sec]")
        print("  python mouse.py scroll <x> <y> <up|down> [clicks]")
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "click":
        x, y = int(sys.argv[2]), int(sys.argv[3])
        button = sys.argv[4] if len(sys.argv) > 4 else "left"
        double = (sys.argv[5] == "double") if len(sys.argv) > 5 else False
        click(x, y, button, double)
        print(f"clicked ({x},{y}) button={button} double={double}")
    elif cmd == "drag":
        x1, y1 = int(sys.argv[2]), int(sys.argv[3])
        x2, y2 = int(sys.argv[4]), int(sys.argv[5])
        duration = float(sys.argv[6]) if len(sys.argv) > 6 else 0.45
        drag(x1, y1, x2, y2, duration)
        print(f"dragged ({x1},{y1}) -> ({x2},{y2})")
    elif cmd == "scroll":
        x, y = int(sys.argv[2]), int(sys.argv[3])
        direction = sys.argv[4]
        clicks = int(sys.argv[5]) if len(sys.argv) > 5 else 3
        scroll(x, y, direction, clicks)
        print(f"scrolled {direction} at ({x},{y}) x{clicks}")
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
