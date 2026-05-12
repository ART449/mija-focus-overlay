"""
mija_sdk._grid — wrappers HTTP para la cuadrícula 16×9, sub-celdas,
mouse real y el inbox de agentes.

Complementa _core.py (que ataca main.py vía subprocess). Aquí usamos
el bridge HTTP en localhost:8000 que ya ataca el overlay directo —
mucho más rápido y sin overhead de subprocess.

Uso típico desde un agente:

    from mija_sdk import point, click, drag, grid_on, clear

    point("B3", "el bug está aquí")
    click("H5")
    drag("A1", "F7")
    grid_on()
"""

from __future__ import annotations

import json
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

DEFAULT_URL          = "http://localhost:8000"
DEFAULT_COLOR_POINT  = "#d97706"   # honey amber — solo señalar
DEFAULT_COLOR_CLICK  = "#10b981"   # green — click real


class MijaError(RuntimeError):
    """El overlay/API no respondió o devolvió error."""


def _post(path: str, body: dict, base: str = DEFAULT_URL, timeout: float = 5.0) -> dict:
    data = json.dumps(body).encode("utf-8")
    req = Request(
        f"{base.rstrip('/')}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        raise MijaError(f"HTTP {e.code} en {path}: {body_text}") from e
    except URLError as e:
        raise MijaError(
            f"No pude conectar con MIJA en {base}. "
            "¿Está corriendo? (python api.py o MIJA_SEÑALADORA.bat)"
        ) from e


def _get(path: str, base: str = DEFAULT_URL, timeout: float = 5.0) -> dict:
    try:
        with urlopen(f"{base.rstrip('/')}{path}", timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (HTTPError, URLError) as e:
        raise MijaError(f"GET {path}: {e}") from e


# ── Health & monitors ─────────────────────────────────────────────────────
def http_status(base: str = DEFAULT_URL) -> dict:
    """Estado del bridge HTTP (no confundir con _core.status que mira pid)."""
    return _get("/status", base)


def is_alive(base: str = DEFAULT_URL) -> bool:
    try:
        return http_status(base).get("components", {}).get("overlay") == "running"
    except MijaError:
        return False


def primary_monitor(base: str = DEFAULT_URL) -> dict:
    return _get("/monitors/primary", base)


def list_monitors(base: str = DEFAULT_URL) -> list[dict]:
    return _get("/monitors", base).get("monitors", [])


# ── Visual: solo señalar ──────────────────────────────────────────────────
def point(
    cell: str,
    label: str = "",
    color: str = DEFAULT_COLOR_POINT,
    duration: float = 8.0,
    monitor: int = 0,
    base: str = DEFAULT_URL,
) -> dict:
    """Pinta un rectángulo pulsante con etiqueta sobre la celda dada.
    No hace click — es "mira ArT, aquí está lo que digo"."""
    return _post("/highlight/cell", {
        "cell": cell,
        "color": color,
        "label": label or cell,
        "duration": duration,
        "monitor": monitor,
    }, base)


def http_clear(base: str = DEFAULT_URL) -> dict:
    return _post("/clear", {}, base)


def grid_on(base: str = DEFAULT_URL) -> dict:
    return _post("/grid/on", {}, base)


def grid_off(base: str = DEFAULT_URL) -> dict:
    return _post("/grid/off", {}, base)


def grid_toggle(base: str = DEFAULT_URL) -> dict:
    return _post("/grid/toggle", {}, base)


# ── Mouse real ────────────────────────────────────────────────────────────
def click(
    cell: str,
    sub: int = 0,
    button: str = "left",
    double: bool = False,
    monitor: int = 0,
    flash: bool = True,
    base: str = DEFAULT_URL,
) -> dict:
    """Click real del SO. `sub` 1..12 para botones chicos dentro de la celda."""
    return _post("/click", {
        "cell": cell,
        "sub": sub,
        "button": button,
        "double": double,
        "monitor": monitor,
        "flash": flash,
    }, base)


def double_click(cell: str, sub: int = 0, monitor: int = 0, base: str = DEFAULT_URL) -> dict:
    return click(cell, sub=sub, double=True, monitor=monitor, base=base)


def right_click(cell: str, sub: int = 0, monitor: int = 0, base: str = DEFAULT_URL) -> dict:
    return click(cell, sub=sub, button="right", monitor=monitor, base=base)


def drag(
    from_cell: str,
    to_cell: str,
    from_sub: int = 0,
    to_sub: int = 0,
    monitor: int = 0,
    duration: float = 0.5,
    base: str = DEFAULT_URL,
) -> dict:
    return _post("/drag", {
        "from_cell": from_cell,
        "to_cell":   to_cell,
        "from_sub":  from_sub,
        "to_sub":    to_sub,
        "monitor":   monitor,
        "duration":  duration,
        "flash":     True,
    }, base)


def scroll(
    direction: str = "up",
    cell: str = "H5",
    clicks: int = 3,
    monitor: int = 0,
    base: str = DEFAULT_URL,
) -> dict:
    return _post("/scroll", {
        "cell": cell,
        "direction": direction,
        "clicks": clicks,
        "monitor": monitor,
    }, base)


# ── Agent inbox (comunicación entre abejas) ───────────────────────────────
def whisper(
    transcript: str,
    parsed_action: Optional[dict] = None,
    context: Optional[dict] = None,
    base: str = DEFAULT_URL,
) -> dict:
    """Loguea contexto al inbox para que otras abejas lo lean."""
    return _post("/agent/inbox", {
        "transcript": transcript,
        "parsed_action": parsed_action,
        "context": context or {},
        "handled_locally": False,
    }, base)


def recent_messages(limit: int = 10, base: str = DEFAULT_URL) -> list[dict]:
    return _get(f"/agent/inbox/recent?limit={limit}", base).get("messages", [])
