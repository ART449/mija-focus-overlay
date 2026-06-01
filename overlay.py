"""
M.I.J.A Focus Overlay
─────────────────────
Transparent, click-through, multi-monitor overlay that draws a coordinate
grid and animated highlights on top of any application. Used by Colmena
agents to point at screen regions via cell names (B3, H5) or pixel coords.

IPC: reads command.json in this directory every 100ms.

Why the rewrite (2026-05-12):
  The previous build relied on `win32gui.FindWindow(None, title)` to attach
  layered-window styles after `overrideredirect(True)`. That call became
  unreliable on Windows 11 because once decorations are stripped, the title
  is not always discoverable. Tkinter's `-transparentcolor "white"` also
  collided with the compositor's anti-aliasing, so the window rendered
  as an opaque white rectangle instead of being transparent.

  Fix:
    1. Get the real HWND directly via `winfo_id()` walking up GetParent().
    2. Drive the layered-window via ctypes (no win32gui dependency).
    3. Use magenta (#ff00ff) as the chroma key — guaranteed never to appear
       on a real screen, so transparency is rock solid.
    4. Add WS_EX_TOOLWINDOW + WS_EX_NOACTIVATE so the overlay never
       steals focus nor shows up in the taskbar / Alt-Tab.
"""

import ctypes
import json
import os
import tkinter as tk

import win32api

# ── DPI Awareness ─────────────────────────────────────────────────────────────
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)   # Per-Monitor V2
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# ── Win32 constants ───────────────────────────────────────────────────────────
GWL_EXSTYLE       = -20
WS_EX_LAYERED     = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOOLWINDOW  = 0x00000080
WS_EX_NOACTIVATE  = 0x08000000

LWA_COLORKEY      = 0x00000001
LWA_ALPHA         = 0x00000002

WS_EX_APPWINDOW   = 0x00040000     # forces taskbar entry — we strip this

SW_HIDE           = 0
SW_SHOWNOACTIVATE = 4
SW_SHOWNA         = 8

# Chroma key for transparency. Magenta is virtually never used in real UI,
# so it won't collide with any pixel we actually want to display.
CHROMA_HEX      = "#ff00ff"          # tkinter color spec
CHROMA_COLORREF = 0x00FF00FF         # Win32 COLORREF (0x00BBGGRR)

# ── Grid config ───────────────────────────────────────────────────────────────
GRID_COLS = 16   # A–P
GRID_ROWS = 9    # 1–9
GRID_LINE_COLOR  = "#3a3a3a"
GRID_LABEL_COLOR = "#00ff66"
GRID_CELL_COLOR  = "#1a8c4a"
GRID_LINE_DASH   = (6, 14)
GRID_HEADER_FONT = ("Consolas", 11, "bold")
GRID_CELL_FONT   = ("Consolas", 8)

# ── Calibration HUD ─────────────────────────────────────────────────────────
HUD_BG           = "#07130d"
HUD_BORDER       = "#22c55e"
HUD_TITLE_COLOR  = "#d7ffe7"
HUD_BODY_COLOR   = "#b5f7c9"
HUD_FONT_TITLE   = ("Consolas", 11, "bold")
HUD_FONT_BODY    = ("Consolas", 9, "bold")

# ── Highlight visuals ─────────────────────────────────────────────────────────
HIGHLIGHT_OUTLINE = "#00ff66"
LABEL_BG          = "#0a0a0a"
LABEL_FG          = "#ffffff"
LABEL_FONT        = ("Consolas", 14, "bold")

_user32 = ctypes.windll.user32


def get_toplevel_hwnd(tk_widget):
    """Walk up the parent chain to find the actual top-level HWND."""
    hwnd = tk_widget.winfo_id()
    parent = _user32.GetParent(hwnd)
    while parent:
        hwnd = parent
        parent = _user32.GetParent(hwnd)
    return hwnd


def configure_overlay_window(hwnd):
    """Layered + click-through + no-taskbar + no-focus styles.

    Windows latches the taskbar entry the moment a window is first made
    visible, so simply setting WS_EX_TOOLWINDOW is not enough — we must
    hide, mutate, then re-show the window for the taskbar to refresh.
    """
    try:
        ex_style = _user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ex_style |= (
            WS_EX_LAYERED
            | WS_EX_TRANSPARENT
            | WS_EX_TOOLWINDOW
            | WS_EX_NOACTIVATE
        )
        ex_style &= ~WS_EX_APPWINDOW   # strip the "show in taskbar" bit
        _user32.ShowWindow(hwnd, SW_HIDE)
        _user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style)
        _user32.SetLayeredWindowAttributes(hwnd, CHROMA_COLORREF, 255, LWA_COLORKEY)
        _user32.ShowWindow(hwnd, SW_SHOWNA)
    except Exception as e:
        print(f"WARN configure_overlay_window: {e}", flush=True)


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
        print(f"DETECTED {len(self.monitors)} MONITORS:", flush=True)
        for i, m in enumerate(self.monitors):
            print(f"  Monitor {i+1}: {m[0]},{m[1]} {m[2]}x{m[3]}", flush=True)

        # Root window stays hidden — only Toplevels are drawn.
        self.root = tk.Tk()
        self.root.withdraw()

        self.grid_visible = False
        self.screens = []

        for i, (mx, my, mw, mh) in enumerate(self.monitors):
            win = tk.Toplevel(self.root)
            win.withdraw()                       # hide while configuring
            win.title(f"MIJAOverlay_{i+1}")
            # Owning the window to the (hidden) root strips it from the
            # taskbar — Windows only puts owner-less top-level windows
            # in the taskbar by default.
            win.transient(self.root)
            win.attributes("-toolwindow", True)  # hide from Alt-Tab
            win.attributes("-topmost", True)
            win.overrideredirect(True)           # no title bar, no borders
            win.geometry(f"{mw}x{mh}+{mx}+{my}")
            win.configure(bg=CHROMA_HEX)

            canvas = tk.Canvas(
                win, bg=CHROMA_HEX, highlightthickness=0,
                bd=0, width=mw, height=mh,
            )
            canvas.pack(fill="both", expand=True)

            rect = canvas.create_rectangle(
                0, 0, 0, 0, outline=HIGHLIGHT_OUTLINE, width=5, state="hidden"
            )
            bubble = canvas.create_rectangle(
                0, 0, 0, 0, fill=LABEL_BG, outline=HIGHLIGHT_OUTLINE,
                width=2, state="hidden"
            )
            text = canvas.create_text(
                0, 0, text="", fill=LABEL_FG,
                font=LABEL_FONT, state="hidden"
            )

            # Materialize → apply layered styles → show.
            win.update_idletasks()
            win.deiconify()
            win.update()

            hwnd = get_toplevel_hwnd(win)
            configure_overlay_window(hwnd)
            print(f"  Overlay {i+1} HWND: {hex(hwnd)}", flush=True)

            self.screens.append({
                "win": win, "canvas": canvas,
                "rect": rect, "bubble": bubble, "text": text,
                "x": mx, "y": my, "w": mw, "h": mh,
                "index": i + 1,
                "pulse_val": 0, "pulse_dir": 1, "pulse_active": False,
                "grid_items": [],
                "hud_items": [],
            })

        self.last_mtime = 0
        self.command_file = os.path.join(self.base_dir, "command.json")
        # La cuadrícula debe quedar fija por defecto; si se apaga en sesión,
        # el reinicio vuelve a dejarla visible.
        self.show_grid()
        self.check_commands()
        self.animate()

    # ── Animation pulse ───────────────────────────────────────────────────────
    def animate(self):
        for s in self.screens:
            if s["pulse_active"]:
                s["pulse_val"] += s["pulse_dir"]
                if s["pulse_val"] > 5 or s["pulse_val"] < 0:
                    s["pulse_dir"] *= -1
                s["canvas"].itemconfig(s["rect"], width=4 + s["pulse_val"])
        self.root.after(50, self.animate)

    # ── Grid draw / hide ──────────────────────────────────────────────────────
    def _draw_grid(self, screen):
        """Draw lettered columns (A–P) and numbered rows (1–9)."""
        mw, mh = screen["w"], screen["h"]
        canvas = screen["canvas"]
        items = []

        cell_w = mw / GRID_COLS
        cell_h = mh / GRID_ROWS

        # Vertical lines + column letters at top
        for col in range(GRID_COLS + 1):
            x = int(col * cell_w)
            line = canvas.create_line(
                x, 0, x, mh,
                fill=GRID_LINE_COLOR, width=1, dash=GRID_LINE_DASH,
            )
            items.append(line)
            if col < GRID_COLS:
                lbl = canvas.create_text(
                    int(x + cell_w / 2), 14,
                    text=chr(65 + col),
                    fill=GRID_LABEL_COLOR,
                    font=GRID_HEADER_FONT,
                )
                items.append(lbl)

        # Horizontal lines + row numbers at left
        for row in range(GRID_ROWS + 1):
            y = int(row * cell_h)
            line = canvas.create_line(
                0, y, mw, y,
                fill=GRID_LINE_COLOR, width=1, dash=GRID_LINE_DASH,
            )
            items.append(line)
            if row < GRID_ROWS:
                lbl = canvas.create_text(
                    14, int(y + cell_h / 2),
                    text=str(row + 1),
                    fill=GRID_LABEL_COLOR,
                    font=GRID_HEADER_FONT,
                )
                items.append(lbl)

        # Small cell coordinate at each cell's top-left corner
        for col in range(GRID_COLS):
            for row in range(GRID_ROWS):
                cx = int(col * cell_w) + 20
                cy = int(row * cell_h) + 22
                cell_lbl = canvas.create_text(
                    cx, cy,
                    text=f"{chr(65+col)}{row+1}",
                    fill=GRID_CELL_COLOR,
                    font=GRID_CELL_FONT,
                    anchor="nw",
                )
                items.append(cell_lbl)

        screen["grid_items"] = items
        print(
            f"Grid ON — {GRID_COLS} cols × {GRID_ROWS} rows  "
            f"({int(cell_w)}×{int(cell_h)} px/celda)",
            flush=True,
        )

    def _hide_grid(self, screen):
        for item in screen["grid_items"]:
            screen["canvas"].delete(item)
        screen["grid_items"] = []
        for item in screen["hud_items"]:
            screen["canvas"].delete(item)
        screen["hud_items"] = []

    def _draw_hud(self, screen):
        """Persistent calibration legend shown on every monitor."""
        canvas = screen["canvas"]
        items = []

        pad = 12
        x0 = 10
        y0 = 10
        x1 = x0 + 324
        y1 = y0 + 104

        panel = canvas.create_rectangle(
            x0, y0, x1, y1,
            fill=HUD_BG,
            outline=HUD_BORDER,
            width=2,
        )
        items.append(panel)

        title = canvas.create_text(
            x0 + pad, y0 + 14,
            text="MIJA FOCUS | GRID FIJA",
            fill=HUD_TITLE_COLOR,
            font=HUD_FONT_TITLE,
            anchor="nw",
        )
        items.append(title)

        lines = [
            f"MONITOR {screen['index']}: {screen['w']}x{screen['h']}  @ {screen['x']},{screen['y']}",
            "CUADRICULA: A-P / 1-9 + A1..P9",
            "AJUSTES: main.py grid_on | grid_off | grid_toggle",
            "CALIBRAR: main.py calibrate",
        ]
        for idx, line in enumerate(lines):
            t = canvas.create_text(
                x0 + pad, y0 + 36 + (idx * 17),
                text=line,
                fill=HUD_BODY_COLOR,
                font=HUD_FONT_BODY,
                anchor="nw",
            )
            items.append(t)

        screen["hud_items"] = items

    def show_grid(self):
        if self.grid_visible:
            return
        for s in self.screens:
            self._draw_grid(s)
            self._draw_hud(s)
        self.grid_visible = True

    def hide_grid(self):
        if not self.grid_visible:
            return
        for s in self.screens:
            self._hide_grid(s)
        self.grid_visible = False

    def toggle_grid(self):
        if self.grid_visible:
            self.hide_grid()
        else:
            self.show_grid()

    # ── Cell → pixel converter ────────────────────────────────────────────────
    def cell_to_rect(self, cell: str, screen_idx: int = 0):
        """Convert 'B3' → (x, y, w, h) absolute pixel coords for monitor."""
        cell = cell.strip().upper()
        col_letter = cell[0]
        row_num    = int(cell[1:])
        col = ord(col_letter) - 65
        row = row_num - 1

        s = self.screens[screen_idx]
        cell_w = s["w"] / GRID_COLS
        cell_h = s["h"] / GRID_ROWS

        x = s["x"] + int(col * cell_w)
        y = s["y"] + int(row * cell_h)
        w = int(cell_w)
        h = int(cell_h)
        return x, y, w, h

    # ── Command loop ──────────────────────────────────────────────────────────
    def check_commands(self):
        try:
            if os.path.exists(self.command_file):
                mtime = os.path.getmtime(self.command_file)
                if mtime > self.last_mtime:
                    self.last_mtime = mtime
                    try:
                        with open(self.command_file, "r", encoding="utf-8") as f:
                            cmd = json.load(f)
                    except PermissionError:
                        # Windows puede bloquear brevemente el archivo durante un replace atomico.
                        self.root.after(100, self.check_commands)
                        return
                    except json.JSONDecodeError:
                        # Si el writer esta a medio cambio, reintentamos en el siguiente tick.
                        self.root.after(100, self.check_commands)
                        return

                    action = cmd.get("action", "")

                    if action == "grid_on":
                        self.show_grid()

                    elif action == "grid_off":
                        self.hide_grid()

                    elif action == "grid_toggle":
                        self.toggle_grid()

                    elif action == "highlight_cell":
                        cell     = cmd.get("cell", "A1")
                        color    = cmd.get("color", HIGHLIGHT_OUTLINE)
                        label    = cmd.get("label", cell)
                        duration = cmd.get("duration", 0)
                        screen_idx = cmd.get("monitor", 1) - 1

                        if not self.grid_visible:
                            self.show_grid()

                        cx, cy, cw, ch = self.cell_to_rect(cell, screen_idx)
                        self._do_highlight(cx, cy, cw, ch, color, label, duration)

                    elif action == "highlight":
                        cx, cy = cmd["x"], cmd["y"]
                        cw, ch = cmd["w"], cmd["h"]
                        label    = cmd.get("label", "FOCUS")
                        duration = cmd.get("duration", 0)
                        color    = cmd.get("color", HIGHLIGHT_OUTLINE)
                        print(f"HIGHLIGHT: {label} at ({cx},{cy})", flush=True)
                        self._do_highlight(cx, cy, cw, ch, color, label, duration)

                    elif action == "clear":
                        self.clear_overlay()

        except Exception as e:
            print(f"DEBUG_ERROR: {e}", flush=True)

        self.root.after(100, self.check_commands)

    def _do_highlight(self, cx, cy, cw, ch, color, label, duration):
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

                s["canvas"].itemconfig(
                    s["text"], text=label, fill=LABEL_FG, state="normal"
                )
                bbox = s["canvas"].bbox(s["text"])
                if bbox:
                    padding = 10
                    bw = bbox[2] - bbox[0] + padding * 2
                    bh = bbox[3] - bbox[1] + padding
                    bx = rx + rw // 2 - bw // 2
                    by = ry - bh - 10
                    s["canvas"].coords(s["bubble"], bx, by, bx + bw, by + bh)
                    s["canvas"].itemconfig(
                        s["bubble"], fill=LABEL_BG, outline=color, state="normal"
                    )
                    s["canvas"].coords(s["text"], bx + bw // 2, by + bh // 2)
                    s["canvas"].itemconfig(s["bubble"], state="normal")
                    s["canvas"].itemconfig(s["text"], state="normal")

    def clear_overlay(self):
        for s in self.screens:
            s["canvas"].itemconfig(s["rect"],   state="hidden")
            s["canvas"].itemconfig(s["text"],   state="hidden")
            s["canvas"].itemconfig(s["bubble"], state="hidden")
            s["pulse_active"] = False


if __name__ == "__main__":
    print("MIJA Focus Overlay (Grid + Multi-DPI + Layered) ONLINE", flush=True)
    app = MIJAOverlay()
    app.root.mainloop()
