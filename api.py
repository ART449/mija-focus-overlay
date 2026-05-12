"""
M.I.J.A Sovereign Bridge — HTTP API
────────────────────────────────────
FastAPI bridge between agents/voice/dashboard and the MIJA Focus Overlay.

Routes:
  GET  /status                — overlay + resident bee health
  GET  /monitors              — list monitors with primary flag
  GET  /monitors/primary      — primary monitor info (1-based index)

  POST /highlight             — highlight by pixel coords (visual only)
  POST /highlight/cell        — highlight by grid cell name (visual only)
  POST /grid/on|off|toggle    — control coordinate grid visibility
  POST /clear                 — clear overlay

  POST /click                 — REAL OS click on a cell (optionally sub-cell)
  POST /drag                  — REAL OS drag between two cells
  POST /scroll                — REAL OS scroll wheel at a cell

  GET  /voice                 — accessibility UI (browser-based STT)
  GET  /templates             — list image templates
"""

import ctypes
import json
import os
import subprocess
import time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

import win32api

GRID_COLS = 16
GRID_ROWS = 9
SUB_COLS  = 4    # sub-grid inside each cell — 4 columns
SUB_ROWS  = 3    # × 3 rows = 12 sub-cells (1..12)

app = FastAPI(title="MIJA Sovereign Bridge")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")


# ── Models ────────────────────────────────────────────────────────────────
class HighlightRequest(BaseModel):
    x: int
    y: int
    w: int
    h: int
    color: str = "green"
    label: str = "WEB_ACTION"
    duration: float = 10.0


class CellRequest(BaseModel):
    cell: str                  # e.g. "B3", "H5"
    color: str = "green"
    label: str = ""
    duration: float = 6.0
    monitor: int = 0           # 0 = auto-resolve to primary


class ClickRequest(BaseModel):
    cell: str
    sub: int = 0               # 0 = cell center; 1..12 = sub-cell
    button: str = "left"       # left | right | middle
    double: bool = False
    monitor: int = 0
    flash: bool = True         # show a brief highlight as visual confirmation


class DragRequest(BaseModel):
    from_cell: str
    to_cell: str
    from_sub: int = 0
    to_sub: int = 0
    monitor: int = 0
    duration: float = 0.5
    flash: bool = True


class ScrollRequest(BaseModel):
    cell: str = "H5"           # default — middle of screen
    direction: str = "up"      # up | down
    clicks: int = 3
    monitor: int = 0


# ── Monitor helpers ───────────────────────────────────────────────────────
def _enumerate_monitors():
    """Return list of monitor dicts. `primary` flags the M2362D-style display
    (the one whose origin is (0,0) — that's how Windows defines primary)."""
    user32 = ctypes.windll.user32
    pw = user32.GetSystemMetrics(0)
    ph = user32.GetSystemMetrics(1)

    monitors = []
    for i, m in enumerate(win32api.EnumDisplayMonitors()):
        x, y, x2, y2 = m[2]
        w, h = x2 - x, y2 - y
        is_primary = (x == 0 and y == 0 and w == pw and h == ph)
        monitors.append({
            "index": i + 1,
            "x": x, "y": y, "w": w, "h": h,
            "primary": is_primary,
        })
    return monitors


def _resolve_monitor(monitor_idx: int) -> dict:
    monitors = _enumerate_monitors()
    if monitor_idx <= 0:
        primary = next((m for m in monitors if m["primary"]), None)
        return primary or monitors[0]
    if monitor_idx > len(monitors):
        raise HTTPException(status_code=400,
                            detail=f"Monitor {monitor_idx} no existe (hay {len(monitors)})")
    return monitors[monitor_idx - 1]


def _primary_monitor_index() -> int:
    for m in _enumerate_monitors():
        if m["primary"]:
            return m["index"]
    return 1


# ── Cell math ─────────────────────────────────────────────────────────────
def _parse_cell(cell: str):
    """'B3' → (col=1, row=2). Raises HTTPException on bad input."""
    cell = cell.strip().upper()
    if len(cell) < 2 or not cell[0].isalpha() or not cell[1:].isdigit():
        raise HTTPException(status_code=400, detail=f"Celda inválida: {cell!r}")
    col = ord(cell[0]) - 65
    row = int(cell[1:]) - 1
    if not (0 <= col < GRID_COLS) or not (0 <= row < GRID_ROWS):
        raise HTTPException(status_code=400, detail=f"Celda fuera de rango: {cell}")
    return col, row


def _cell_center(cell: str, monitor_idx: int = 0, sub: int = 0):
    """Resolve a cell (and optional sub-cell 1..12) to absolute pixel center."""
    m = _resolve_monitor(monitor_idx)
    col, row = _parse_cell(cell)

    cell_w = m["w"] / GRID_COLS
    cell_h = m["h"] / GRID_ROWS
    x0 = m["x"] + col * cell_w
    y0 = m["y"] + row * cell_h

    if sub <= 0:
        cx = int(x0 + cell_w / 2)
        cy = int(y0 + cell_h / 2)
    else:
        if not (1 <= sub <= SUB_COLS * SUB_ROWS):
            raise HTTPException(status_code=400,
                                detail=f"Sub-celda fuera de rango: {sub} (1..{SUB_COLS*SUB_ROWS})")
        sub_col = (sub - 1) % SUB_COLS
        sub_row = (sub - 1) // SUB_COLS
        sub_w = cell_w / SUB_COLS
        sub_h = cell_h / SUB_ROWS
        cx = int(x0 + sub_col * sub_w + sub_w / 2)
        cy = int(y0 + sub_row * sub_h + sub_h / 2)

    return cx, cy, m["index"]


# ── Overlay IPC (direct write, skips main.py for speed) ───────────────────
def _send_overlay(cmd: dict):
    tmp   = os.path.join(BASE_DIR, "command.json.tmp")
    final = os.path.join(BASE_DIR, "command.json")
    with open(tmp, "w") as f:
        json.dump(cmd, f)
    os.replace(tmp, final)


def _flash_cell(cell: str, monitor: int, color: str, label: str, duration: float = 1.2):
    _send_overlay({
        "action": "highlight_cell",
        "cell": cell,
        "color": color,
        "label": label,
        "duration": duration,
        "monitor": monitor,
    })


# ── Status / monitor endpoints ────────────────────────────────────────────
@app.get("/status")
def get_status():
    overlay_active = os.path.exists(os.path.join(BASE_DIR, "overlay.pid"))
    bee_active = os.path.exists(os.path.join(BASE_DIR, "bee.pid"))
    return {
        "status": "online",
        "components": {
            "overlay": "running" if overlay_active else "stopped",
            "resident_bee": "running" if bee_active else "stopped",
        },
        "version": "2.0-accesibilidad",
    }


@app.get("/monitors")
def list_monitors():
    return {"monitors": _enumerate_monitors()}


@app.get("/monitors/primary")
def get_primary():
    monitors = _enumerate_monitors()
    primary = next((m for m in monitors if m["primary"]), monitors[0])
    return primary


# ── Visual-only endpoints ─────────────────────────────────────────────────
@app.post("/highlight")
def post_highlight(req: HighlightRequest):
    try:
        cmd = [
            "python", "main.py", "highlight",
            str(req.x), str(req.y), str(req.w), str(req.h),
            req.color, req.label, str(req.duration)
        ]
        subprocess.Popen(cmd, cwd=BASE_DIR)
        return {"status": "success", "message": f"Highlight at ({req.x}, {req.y})"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/highlight/cell")
def post_highlight_cell(req: CellRequest):
    monitor = req.monitor if req.monitor > 0 else _primary_monitor_index()
    label = req.label or req.cell
    _send_overlay({
        "action": "highlight_cell",
        "cell": req.cell,
        "color": req.color,
        "label": label,
        "duration": req.duration,
        "monitor": monitor,
    })
    return {"status": "success", "cell": req.cell, "monitor": monitor}


@app.post("/grid/on")
def grid_on():
    _send_overlay({"action": "grid_on"})
    return {"status": "success", "grid": "on"}


@app.post("/grid/off")
def grid_off():
    _send_overlay({"action": "grid_off"})
    return {"status": "success", "grid": "off"}


@app.post("/grid/toggle")
def grid_toggle():
    _send_overlay({"action": "grid_toggle"})
    return {"status": "success", "grid": "toggled"}


@app.post("/clear")
def post_clear():
    _send_overlay({"action": "clear"})
    return {"status": "success"}


# ── Real mouse action endpoints ───────────────────────────────────────────
@app.post("/click")
def post_click(req: ClickRequest):
    """Mueve el cursor a la celda y dispara un click real del sistema operativo.
    El overlay es click-through, así que el evento pasa limpio a la app de abajo."""
    cx, cy, monitor = _cell_center(req.cell, req.monitor, req.sub)

    if req.flash:
        label = f"{'DOBLE ' if req.double else ''}CLICK {req.cell}"
        if req.sub:
            label += f".{req.sub}"
        _flash_cell(req.cell, monitor, color="#10b981", label=label, duration=1.0)
        time.sleep(0.15)   # tiny lead-in so user sees the highlight first

    subprocess.Popen([
        "python", "mouse.py", "click",
        str(cx), str(cy), req.button,
        "double" if req.double else "single",
    ], cwd=BASE_DIR)

    return {
        "status": "success",
        "cell": req.cell, "sub": req.sub,
        "x": cx, "y": cy, "monitor": monitor,
        "button": req.button, "double": req.double,
    }


@app.post("/drag")
def post_drag(req: DragRequest):
    """Arrastra desde una celda hasta otra (mouse-down → move → mouse-up)."""
    x1, y1, monitor = _cell_center(req.from_cell, req.monitor, req.from_sub)
    x2, y2, _       = _cell_center(req.to_cell,   req.monitor, req.to_sub)

    if req.flash:
        _flash_cell(req.from_cell, monitor, color="#06b6d4",
                    label=f"DESDE {req.from_cell}", duration=0.8)
        time.sleep(0.1)
        _flash_cell(req.to_cell, monitor, color="#10b981",
                    label=f"HASTA {req.to_cell}", duration=1.8)

    subprocess.Popen([
        "python", "mouse.py", "drag",
        str(x1), str(y1), str(x2), str(y2), str(req.duration),
    ], cwd=BASE_DIR)

    return {
        "status": "success",
        "from": req.from_cell, "to": req.to_cell,
        "from_xy": [x1, y1], "to_xy": [x2, y2],
        "monitor": monitor,
    }


@app.post("/scroll")
def post_scroll(req: ScrollRequest):
    cx, cy, monitor = _cell_center(req.cell, req.monitor, 0)
    subprocess.Popen([
        "python", "mouse.py", "scroll",
        str(cx), str(cy), req.direction, str(req.clicks),
    ], cwd=BASE_DIR)
    return {
        "status": "success",
        "cell": req.cell, "direction": req.direction,
        "clicks": req.clicks, "monitor": monitor,
    }


# ── Static UI ─────────────────────────────────────────────────────────────
@app.get("/voice")
def voice_ui():
    path = os.path.join(STATIC_DIR, "voice.html")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="voice.html not found")
    return FileResponse(path)


@app.get("/templates")
def list_templates():
    template_dir = os.path.join(BASE_DIR, "templates")
    if not os.path.exists(template_dir):
        return {"templates": []}
    files = [f.replace(".png", "") for f in os.listdir(template_dir) if f.endswith(".png")]
    return {"templates": files}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
