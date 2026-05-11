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
