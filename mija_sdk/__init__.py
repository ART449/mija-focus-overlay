"""
MIJA Focus Overlay — AI Agent Visual Guidance SDK
──────────────────────────────────────────────────

Dos modos de uso:

1) Por pixel (vía main.py subprocess — original):

    from mija_sdk import highlight, find, match, calibrate
    highlight(500, 300, 200, 100, "green", "CLICK HERE", 5)
    find("Brave")
    match("save_btn")

2) Por celda + mouse real (vía HTTP bridge — recomendado para agentes):

    from mija_sdk import point, click, drag, grid_on
    point("B3", "el bug está aquí")
    click("H5")
    drag("A1", "F7")
    grid_on()

Para detalles ver `AGENTES.md`.
"""

# ── API original (subprocess → main.py) ──────────────────────────────────
from mija_sdk._core import (
    highlight,
    clear,
    find,
    calibrate,
    save_template,
    match,
    status,
    stop,
)

# ── API por celda + HTTP bridge ──────────────────────────────────────────
from mija_sdk._grid import (
    # health
    http_status,
    is_alive,
    primary_monitor,
    list_monitors,
    # visual
    point,
    http_clear,
    grid_on,
    grid_off,
    grid_toggle,
    # mouse real
    click,
    double_click,
    right_click,
    drag,
    scroll,
    # inbox
    whisper,
    recent_messages,
    # error
    MijaError,
)

__version__ = "2.0.0"
__all__ = [
    # original
    "highlight", "clear", "find", "calibrate",
    "save_template", "match", "status", "stop",
    # nuevo: health
    "http_status", "is_alive", "primary_monitor", "list_monitors",
    # nuevo: visual
    "point", "http_clear", "grid_on", "grid_off", "grid_toggle",
    # nuevo: mouse
    "click", "double_click", "right_click", "drag", "scroll",
    # nuevo: inbox
    "whisper", "recent_messages",
    # error
    "MijaError",
]
