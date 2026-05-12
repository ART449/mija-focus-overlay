"""
M.I.J.A Sovereign Bridge — HTTP API
────────────────────────────────────
FastAPI bridge between agents/voice/dashboard and the MIJA Focus Overlay.

Routes:
  GET  /status              — overlay + resident bee health
  GET  /monitors            — list monitors with primary flag
  GET  /monitors/primary    — primary monitor index (1-based)
  POST /highlight           — highlight by pixel coords
  POST /highlight/cell      — highlight by grid cell name (B3, H5...)
  POST /grid/on|off|toggle  — control coordinate grid visibility
  POST /clear               — clear overlay
  GET  /voice               — accessibility UI (browser-based STT)
  GET  /templates           — list image templates
"""

import ctypes
import json
import os
import subprocess

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

import win32api

app = FastAPI(title="MIJA Sovereign Bridge")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")


class HighlightRequest(BaseModel):
    x: int
    y: int
    w: int
    h: int
    color: str = "green"
    label: str = "WEB_ACTION"
    duration: float = 10.0


class CellRequest(BaseModel):
    cell: str               # e.g. "B3", "H5"
    color: str = "green"
    label: str = ""         # empty → use cell name
    duration: float = 6.0
    monitor: int = 0        # 0 = auto-resolve to primary


def _enumerate_monitors():
    """Return list of monitor dicts with primary flag. Primary is the one
    whose top-left is (0,0) — that's how Windows defines it."""
    user32 = ctypes.windll.user32
    primary_w = user32.GetSystemMetrics(0)
    primary_h = user32.GetSystemMetrics(1)

    monitors = []
    for i, m in enumerate(win32api.EnumDisplayMonitors()):
        x, y, x2, y2 = m[2]
        w, h = x2 - x, y2 - y
        is_primary = (x == 0 and y == 0 and w == primary_w and h == primary_h)
        monitors.append({
            "index": i + 1,
            "x": x, "y": y, "w": w, "h": h,
            "primary": is_primary,
        })
    return monitors


def _primary_monitor_index():
    for m in _enumerate_monitors():
        if m["primary"]:
            return m["index"]
    return 1   # fallback


@app.get("/status")
def get_status():
    overlay_active = os.path.exists(os.path.join(BASE_DIR, "overlay.pid"))
    bee_active = os.path.exists(os.path.join(BASE_DIR, "bee.pid"))
    return {
        "status": "online",
        "components": {
            "overlay": "running" if overlay_active else "stopped",
            "resident_bee": "running" if bee_active else "stopped"
        }
    }


@app.get("/monitors")
def list_monitors():
    """List all detected monitors. The one with `primary: true` is M2362D-style
    primary (the user's main visual focus)."""
    return {"monitors": _enumerate_monitors()}


@app.get("/monitors/primary")
def get_primary():
    """Return the 1-based index of the primary monitor.
    Agents should use this index when calling /highlight/cell."""
    monitors = _enumerate_monitors()
    primary = next((m for m in monitors if m["primary"]), monitors[0])
    return primary


@app.post("/highlight")
def post_highlight(req: HighlightRequest):
    try:
        cmd = [
            "python", "main.py", "highlight",
            str(req.x), str(req.y), str(req.w), str(req.h),
            req.color, req.label, str(req.duration)
        ]
        subprocess.Popen(cmd, cwd=BASE_DIR)
        return {"status": "success", "message": f"Highlight sent to ({req.x}, {req.y})"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/highlight/cell")
def post_highlight_cell(req: CellRequest):
    """Highlight a grid cell by name. Set monitor=0 (default) to auto-resolve
    to the primary monitor."""
    try:
        monitor = req.monitor if req.monitor > 0 else _primary_monitor_index()
        label = req.label or req.cell
        cmd = [
            "python", "main.py", "cell",
            req.cell, req.color, label,
            str(req.duration), str(monitor),
        ]
        subprocess.Popen(cmd, cwd=BASE_DIR)
        return {
            "status": "success",
            "message": f"Highlighting cell {req.cell}",
            "monitor": monitor,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/grid/on")
def grid_on():
    subprocess.Popen(["python", "main.py", "grid_on"], cwd=BASE_DIR)
    return {"status": "success", "grid": "on"}


@app.post("/grid/off")
def grid_off():
    subprocess.Popen(["python", "main.py", "grid_off"], cwd=BASE_DIR)
    return {"status": "success", "grid": "off"}


@app.post("/grid/toggle")
def grid_toggle():
    subprocess.Popen(["python", "main.py", "grid_toggle"], cwd=BASE_DIR)
    return {"status": "success", "grid": "toggled"}


@app.post("/clear")
def post_clear():
    subprocess.Popen(["python", "main.py", "clear"], cwd=BASE_DIR)
    return {"status": "success"}


@app.get("/voice")
def voice_ui():
    """Serve the accessibility voice UI (browser-based STT)."""
    path = os.path.join(STATIC_DIR, "voice.html")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="voice.html not found")
    return FileResponse(path)


@app.get("/templates")
def list_templates():
    template_dir = os.path.join(BASE_DIR, "templates")
    files = [f.replace(".png", "") for f in os.listdir(template_dir) if f.endswith(".png")]
    return {"templates": files}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
