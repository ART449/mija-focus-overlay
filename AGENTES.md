# MIJA · Guía rápida para agentes IA

> **Para quién**: abejas de la Colmena (Memo, Codex, ChatGPT_CTO, Kimi, Cetacea, Mimo, Meli, Melissa, Mercuri Bee, Aurea, Kibee_UI, etc.) y cualquier asistente que necesite **señalar, click-ear o arrastrar** en la pantalla de ArT.

---

## 1. ¿Qué es MIJA?

Un overlay transparente que vive sobre todas las ventanas de Windows. Te deja:

- **Señalar** una región (rectángulo verde pulsante + etiqueta de texto) sin tocar nada.
- **Hacer click / doble click / click derecho** real del sistema operativo.
- **Arrastrar** entre dos puntos.
- **Hacer scroll** del mouse.

Las coordenadas son una **cuadrícula 16×9** (columnas `A → P`, filas `1 → 9`). No pelees con pixeles — di `B3` y MIJA resuelve.

Si necesitas precisión adentro de una celda (un botón muy chico), la celda se subdivide en **12 sub-celdas (4×3)** numeradas `1 → 12`.

---

## 2. Arrancar MIJA

Antes de usar el SDK, asegúrate que esté corriendo:

```bat
C:\BYFLOW\MIJA_FOCUS_OVERLAY\MIJA_SEÑALADORA.bat
```

Esto levanta:
- `overlay.py` — la ventana transparente click-through
- `api.py` — bridge HTTP en `localhost:8000`
- `resident_bee.py` — abejita 🐝 en el taskbar (opcional)

Verifica desde Python:

```python
import mija_sdk as mija
mija.is_alive()        # True si overlay y API responden
mija.status()          # detalle completo
```

---

## 3. Comandos esenciales

### Señalar (no toca nada)

```python
import mija_sdk as mija

# "Mira ArT, aquí está lo que digo"
mija.point("B3", "el bug está aquí")
mija.point("H5", "este botón abre la config", duration=5.0)

# Sin etiqueta = solo el nombre de la celda
mija.point("C7")
```

### Click real

```python
mija.click("H5")                     # click izquierdo
mija.double_click("C7")              # abre algo
mija.right_click("D4")               # menú contextual

# Para botones chicos: sub-celda 1..12 dentro de B3
mija.click("B3", sub=5)              # centro-izquierda de B3
```

### Arrastrar y scroll

```python
mija.drag("A1", "F7")                # selecciona texto, mueve ventanas
mija.scroll("up", cell="H5")         # scroll arriba sobre H5
mija.scroll("down", clicks=10)       # 10 notches abajo
```

### Cuadrícula visible (debug)

```python
mija.grid_on()      # pinta la grilla A-P / 1-9 sobre la pantalla
mija.grid_off()
mija.grid_toggle()
```

### Limpiar

```python
mija.http_clear()   # quita cualquier highlight, mantiene la app viva
                    # (clear() del módulo original también existe, ese va vía main.py)
```

---

## 4. Patrones de uso

### Patrón "explícale a ArT antes de actuar"

```python
mija.point("H5", "voy a abrir Settings, dame 1s")
time.sleep(1.0)
mija.click("H5")
```

### Patrón "confirma antes de algo destructivo"

```python
mija.point("D2", "este botón borra todo — ¿OK?", duration=20.0)
# espera respuesta de ArT antes de tocar nada
```

### Patrón "guía paso a paso"

```python
mija.point("B3", "1. busca este icono")
time.sleep(2)
mija.point("H4", "2. dale click")
time.sleep(2)
mija.point("J7", "3. ahora aquí")
```

### Patrón "ejecuta directo"

```python
# Para acciones repetitivas o automáticas, sin teatro
mija.click("H5")
mija.drag("A1", "F7")
mija.click("P9")
```

---

## 5. Sistema de coordenadas

### Celdas principales (16×9)

```
   A   B   C   D   E   F   G   H   I   J   K   L   M   N   O   P
1 [A1][B1][C1][D1][E1][F1][G1][H1][I1][J1][K1][L1][M1][N1][O1][P1]
2 [A2][B2][C2][D2][E2][F2][G2][H2][I2][J2][K2][L2][M2][N2][O2][P2]
...
9 [A9][B9][C9][D9][E9][F9][G9][H9][I9][J9][K9][L9][M9][N9][O9][P9]
```

### Sub-celdas dentro de una celda (4×3)

```
 1  2  3  4
 5  6  7  8
 9 10 11 12
```

Ejemplo: `mija.click("B3", sub=5)` aterriza en la mitad-izquierda de la celda B3 (donde típicamente hay un botón chico).

### Multi-monitor

- `monitor=0` (default) = primario (donde ArT tiene su foco visual)
- `monitor=1, 2, 3...` = índice 1-based según `EnumDisplayMonitors`
- `mija.primary_monitor()` te dice cuál es el primario y sus dimensiones

---

## 6. Inbox de agentes

Si tienes contexto que otra abeja debería ver, escríbelo al inbox:

```python
mija.whisper("Memo terminó el fix de overlay — revisa commit 992350b")
# se guarda en agent_inbox/YYYY-MM-DD.jsonl

# La siguiente abeja lee:
for msg in mija.recent_messages(limit=20):
    print(msg["ts"], msg["transcript"])
```

Es **append-only**, persistente por día, accesible vía HTTP también:

- `POST /agent/inbox`        guardar
- `GET  /agent/inbox/recent` leer

---

## 7. Errores comunes

| Síntoma | Causa | Fix |
|---|---|---|
| `MijaError: No pude conectar` | overlay/api no corriendo | corre `MIJA_SEÑALADORA.bat` |
| Highlight no aparece | overlay zombie tras horas | reinicia overlay |
| Click en lugar equivocado | monitor incorrecto | usa `monitor=0` o llama `primary_monitor()` primero |
| Web Speech no entiende celda | (no aplica a agentes) | usa el SDK directo, no la UI |

---

## 8. URL del API (para no-Python)

Cualquier abeja que no use Python puede hablarle por HTTP:

```bash
curl -X POST http://localhost:8000/highlight/cell \
  -H "Content-Type: application/json" \
  -d '{"cell":"B3","label":"el bug","duration":8}'
```

Endpoints completos: ver `api.py` o `GET http://localhost:8000/docs` (FastAPI auto-genera Swagger).

---

## 9. Filosofía

> *MIJA es la mano del agente. Si una abeja necesita decirte algo que vive en
> tu pantalla, no te lo describe con palabras — te lo apunta. Si una abeja
> necesita ejecutar algo, te muestra qué va a tocar antes de tocarlo.*

Esto cambia la dinámica humano↔agente: pasamos de **explicar** a **mostrar**.
Para ArT (baja visión, neurodivergencia visual-espacial) y para los demás,
"ve esto" siempre será más rápido que "el tercer botón empezando por la
izquierda en la barra de arriba".

— IArtLabs, La Colmena
