import ctypes
import tkinter as tk
import json
import os
import win32gui
import win32con
import win32api

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()

GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020


def set_click_through(hwnd):
    try:
        styles = win32gui.GetWindowLong(hwnd, GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, GWL_EXSTYLE, styles | WS_EX_LAYERED | WS_EX_TRANSPARENT)
    except Exception as e:
        print(f"Error en Click-Through: {e}")


def get_monitor_rects():
    rects = []
    for m in win32api.EnumDisplayMonitors():
        x, y, x2, y2 = m[2]
        rects.append((x, y, x2 - x, y2 - y))
    return rects


class MIJAOverlay:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.pid_file = os.path.join(self.base_dir, "overlay.pid")
        with open(self.pid_file, "w") as f:
            f.write(str(os.getpid()))

        self.monitors = get_monitor_rects()
        print(f"DETECTED {len(self.monitors)} MONITORS:")
        for i, m in enumerate(self.monitors):
            print(f"  Monitor {i+1}: {m[0]},{m[1]} {m[2]}x{m[3]}")

        self.root = tk.Tk()
        self.root.title("MIJA_Focus_Overlay_CTRL")
        self.root.geometry("1x1+0+0")
        self.root.configure(bg="white")
        self.root.attributes("-alpha", 0)

        self.screens = []
        for i, (mx, my, mw, mh) in enumerate(self.monitors):
            win = tk.Toplevel(self.root)
            win.title(f"MIJA_Focus_Overlay_{i+1}")
            win.overrideredirect(True)
            win.attributes("-topmost", True)
            win.config(bg="white")
            win.attributes("-transparentcolor", "white")
            win.geometry(f"{mw}x{mh}+{mx}+{my}")

            canvas = tk.Canvas(win, bg="white", highlightthickness=0, width=mw, height=mh)
            canvas.pack()

            rect = canvas.create_rectangle(0, 0, 0, 0, outline="green", width=5, state="hidden")
            bubble = canvas.create_rectangle(0, 0, 0, 0, fill="black", outline="white", width=2, state="hidden")
            text = canvas.create_text(0, 0, text="", fill="white", font=("Arial", 12, "bold"), state="hidden")

            win.update()
            hwnd = win32gui.FindWindow(None, f"MIJA_Focus_Overlay_{i+1}")
            if hwnd:
                set_click_through(hwnd)

            self.screens.append({
                "win": win,
                "canvas": canvas,
                "rect": rect,
                "bubble": bubble,
                "text": text,
                "x": mx, "y": my, "w": mw, "h": mh,
                "pulse_val": 0,
                "pulse_dir": 1,
                "pulse_active": False,
            })

        self.last_mtime = 0
        self.command_file = os.path.join(self.base_dir, "command.json")
        self.check_commands()
        self.animate()

    def animate(self):
        for s in self.screens:
            if s["pulse_active"]:
                s["pulse_val"] += s["pulse_dir"]
                if s["pulse_val"] > 5 or s["pulse_val"] < 0:
                    s["pulse_dir"] *= -1
                s["canvas"].itemconfig(s["rect"], width=4 + s["pulse_val"])
        self.root.after(50, self.animate)

    def check_commands(self):
        try:
            if os.path.exists(self.command_file):
                mtime = os.path.getmtime(self.command_file)
                if mtime > self.last_mtime:
                    self.last_mtime = mtime
                    with open(self.command_file, "r") as f:
                        cmd = json.load(f)

                    if cmd["action"] == "highlight":
                        cx, cy, cw, ch = cmd["x"], cmd["y"], cmd["w"], cmd["h"]
                        label = cmd.get("label", "FOCUS")
                        duration = cmd.get("duration", 0)
                        color = cmd.get("color", "green")
                        print(f"HIGHLIGHT: {label} at ({cx},{cy})")

                        for s in self.screens:
                            mx, my, mw, mh = s["x"], s["y"], s["w"], s["h"]
                            if cx + cw > mx and cx < mx + mw and cy + ch > my and cy < my + mh:
                                rx = max(cx - mx, 0)
                                ry = max(cy - my, 0)
                                rw = min(cx + cw, mx + mw) - max(cx, mx)
                                rh = min(cy + ch, my + mh) - max(cy, my)

                                s["canvas"].coords(s["rect"], rx, ry, rx + rw, ry + rh)
                                s["canvas"].itemconfig(s["rect"], outline=color, state="normal")
                                s["pulse_active"] = True

                                if duration > 0:
                                    self.root.after(int(duration * 1000), self.clear_overlay)

                                s["canvas"].itemconfig(s["text"], text=label, fill="white", state="normal")
                                bbox = s["canvas"].bbox(s["text"])
                                if bbox:
                                    padding = 10
                                    bw = bbox[2] - bbox[0] + padding * 2
                                    bh = bbox[3] - bbox[1] + padding
                                    bx = rx + rw // 2 - bw // 2
                                    by = ry - bh - 10
                                    s["canvas"].coords(s["bubble"], bx, by, bx + bw, by + bh)
                                    s["canvas"].itemconfig(s["bubble"], fill="#1a1a1a", outline=color, state="normal")
                                    s["canvas"].coords(s["text"], bx + bw // 2, by + bh // 2)
                                    s["canvas"].itemconfig(s["bubble"], state="normal")
                                    s["canvas"].itemconfig(s["text"], state="normal")

                    elif cmd["action"] == "clear":
                        self.clear_overlay()
        except Exception as e:
            print(f"DEBUG_ERROR: {e}", flush=True)
        self.root.after(100, self.check_commands)

    def clear_overlay(self):
        for s in self.screens:
            s["canvas"].itemconfig(s["rect"], state="hidden")
            s["canvas"].itemconfig(s["text"], state="hidden")
            s["canvas"].itemconfig(s["bubble"], state="hidden")
            s["pulse_active"] = False


if __name__ == "__main__":
    print("MIJA Focus Overlay (Per-Monitor Multi-DPI) ONLINE", flush=True)
    app = MIJAOverlay()
    app.root.mainloop()
