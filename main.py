import sys
import json
import os
from vision import capture_screen

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COMMAND_FILE = os.path.join(BASE_DIR, "command.json")

def send_command(data):
    """Writes a command to the JSON file for the overlay to read using an atomic replace."""
    temp_file = COMMAND_FILE + ".tmp"
    with open(temp_file, "w") as f:
        json.dump(data, f)
    os.replace(temp_file, COMMAND_FILE)

def main():
    if len(sys.argv) < 2:
        print("M.I.J.A Focus Controller")
        print("Usage:")
        print("  python main.py highlight <x> <y> <w> <h> [color] [label] [duration]")
        print("  python main.py cell <CELL> [color] [label] [duration] [monitor]  e.g. cell B3 green")
        print("  python main.py grid_on       -- mostrar cuadrícula fija + HUD")
        print("  python main.py grid_off      -- ocultar cuadrícula")
        print("  python main.py grid_toggle   -- alternar cuadrícula")
        print("  python main.py calibrate     -- grid fija + marco por monitor")
        print("  python main.py clear")
        print("  python main.py capture")
        print("  python main.py test")
        return

    cmd = sys.argv[1].lower()
    
    if cmd == "highlight":
        if len(sys.argv) < 6:
            print("Error: Missing coordinates. (x y w h)")
            return
        data = {
            "action": "highlight",
            "x": int(sys.argv[2]),
            "y": int(sys.argv[3]),
            "w": int(sys.argv[4]),
            "h": int(sys.argv[5]),
            "color": sys.argv[6] if len(sys.argv) > 6 else "green",
            "label": sys.argv[7] if len(sys.argv) > 7 else "FOCUS",
            "duration": float(sys.argv[8]) if len(sys.argv) > 8 else 5.0 # Default 5s
        }
        send_command(data)
        print(f"SENT: Highlight at ({data['x']}, {data['y']}) Color: {data['color']}")

    # ── Grid commands ──────────────────────────────────────────────────────────
    elif cmd == "grid_on":
        send_command({"action": "grid_on"})
        print("SENT: Grid ON  (cols A–P, rows 1–9)")

    elif cmd == "grid_off":
        send_command({"action": "grid_off"})
        print("SENT: Grid OFF")

    elif cmd == "grid_toggle":
        send_command({"action": "grid_toggle"})
        print("SENT: Grid TOGGLE")

    # ── Highlight by cell name ─────────────────────────────────────────────────
    elif cmd == "cell":
        if len(sys.argv) < 3:
            print("Usage: python main.py cell <CELL> [color] [label] [duration] [monitor]")
            print("  e.g. python main.py cell B3 green")
            return
        cell     = sys.argv[2].upper()
        color    = sys.argv[3] if len(sys.argv) > 3 else "green"
        label    = sys.argv[4] if len(sys.argv) > 4 else cell
        duration = float(sys.argv[5]) if len(sys.argv) > 5 else 6.0
        monitor  = int(sys.argv[6]) if len(sys.argv) > 6 else 1
        send_command({
            "action": "highlight_cell",
            "cell": cell,
            "color": color,
            "label": label,
            "duration": duration,
            "monitor": monitor,
        })
        print(f"SENT: Highlight cell {cell}  color={color}  label={label}")

    elif cmd == "clear":
        send_command({"action": "clear"})
        print("SENT: Clear Overlay")

    elif cmd == "capture":
        path = capture_screen()
        print(f"SCREENSHOT: {path}")

    elif cmd == "test":
        # Simulate a sequence
        print("Running Test Sequence...")
        import time
        send_command({"action": "highlight", "x": 100, "y": 100, "w": 300, "h": 100, "color": "green", "label": "TEST_VERDE"})
        time.sleep(2)
        send_command({"action": "highlight", "x": 500, "y": 300, "w": 200, "h": 200, "color": "red", "label": "TEST_ROJO"})
        time.sleep(2)
        send_command({"action": "clear"})
        print("Test Complete.")

    elif cmd == "find":
        if len(sys.argv) < 3:
            print("Usage: python main.py find <Window Title>")
            return
        from vision import get_window_rect
        title = " ".join(sys.argv[2:])
        rect = get_window_rect(title)
        if rect:
            x, y, w, h = rect
            send_command({"action": "highlight", "x": x, "y": y, "w": w, "h": h, "color": "yellow", "label": title})
            print(f"FOUND: {title} at {rect}")
        else:
            print(f"NOT FOUND: {title}")

    elif cmd == "calibrate":
        print("Iniciando Calibración Multi-Monitor...")
        send_command({"action": "grid_on"})
        import win32api
        monitors = win32api.EnumDisplayMonitors()
        for i, m in enumerate(monitors):
            rect = m[2]
            x, y, x2, y2 = rect
            w, h = x2 - x, y2 - y
            # Pintar un cuadro en el centro de cada monitor detectado
            data = {
                "action": "highlight",
                "x": x + w//4,
                "y": y + h//4,
                "w": w//2,
                "h": h//2,
                "color": "yellow",
                "label": f"MONITOR_{i+1}"
            }
            send_command(data)
            print(f"Monitor {i+1} calibrado: {rect}")
            import time
            time.sleep(1.5) # Pausa para que el usuario vea cada monitor
        print("Calibración completada. Grid fija y HUD visibles.")

    elif cmd == "save_template":
        if len(sys.argv) < 7:
            print("Usage: python main.py save_template <name> <x> <y> <w> <h>")
            return
        name = sys.argv[2]
        x, y, w, h = int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
        from PIL import ImageGrab
        img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
        save_path = os.path.join(BASE_DIR, "templates", name + ".png")
        img.save(save_path)
        print(f"TEMPLATE SAVED: {save_path}")

    elif cmd == "match":
        if len(sys.argv) < 3:
            print("Usage: python main.py match <template_name> [color] [threshold] [duration]")
            return
        name = sys.argv[2]
        color = sys.argv[3] if len(sys.argv) > 3 else "green"
        threshold = float(sys.argv[4]) if len(sys.argv) > 4 else 0.8
        duration = float(sys.argv[5]) if len(sys.argv) > 5 else 5.0

        from matcher import find_template_on_screen
        res = find_template_on_screen(name + ".png", threshold=threshold)
        if res:
            x, y, w, h = res
            send_command({
                "action": "highlight", 
                "x": x, "y": y, "w": w, "h": h, 
                "color": color, 
                "label": f"MATCH: {name}",
                "duration": duration
            })
            print(f"MATCH FOUND: {res} Conf: {threshold}")
        else:
            print("MATCH NOT FOUND")

    elif cmd == "stop":
        print("Stopping MIJA Components...")
        for pid_name in ["overlay.pid", "bee.pid"]:
            pid_path = os.path.join(BASE_DIR, pid_name)
            if os.path.exists(pid_path):
                try:
                    with open(pid_path, "r") as f:
                        pid = f.read().strip()
                    os.system(f"taskkill /F /PID {pid} >nul 2>&1")
                    os.remove(pid_path)
                    print(f"Terminated {pid_name} (PID {pid})")
                except Exception as e:
                    print(f"Error terminating {pid_name}: {e}")

        # Fallback: kill by window title (wildcard para multi-monitor)
        os.system(
            'powershell -Command "'
            'Get-Process | Where-Object {$_.MainWindowTitle -like \'MIJA_Focus_Overlay*\'} '
            '| Stop-Process -Force" >nul 2>&1'
        )
        os.system('taskkill /F /FI "WINDOWTITLE eq MIJA_Bee_Button" >nul 2>&1')

        if os.path.exists(COMMAND_FILE):
            os.remove(COMMAND_FILE)
        print("MIJA Components Stopped.")

if __name__ == "__main__":
    main()
