from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import os
import json

app = FastAPI(title="MIJA Sovereign Bridge")

# Permitir que el Dashboard (React) se conecte sin problemas
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class HighlightRequest(BaseModel):
    x: int
    y: int
    w: int
    h: int
    color: str = "green"
    label: str = "WEB_ACTION"
    duration: float = 10.0

class CellRequest(BaseModel):
    cell: str          # e.g. "B3", "H5"
    color: str = "green"
    label: str = ""    # vacío = usa el nombre de la celda
    duration: float = 6.0
    monitor: int = 1

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
    """Highlight a grid cell by name — agents use this. e.g. POST /highlight/cell  {'cell':'B3'}"""
    try:
        label = req.label or req.cell
        cmd = [
            "python", "main.py", "cell",
            req.cell, req.color, label,
            str(req.duration), str(req.monitor),
        ]
        subprocess.Popen(cmd, cwd=BASE_DIR)
        return {"status": "success", "message": f"Highlighting cell {req.cell}"}
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

@app.get("/templates")
def list_templates():
    template_dir = os.path.join(BASE_DIR, "templates")
    files = [f.replace(".png", "") for f in os.listdir(template_dir) if f.endswith(".png")]
    return {"templates": files}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
