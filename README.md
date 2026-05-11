# 🐝 MIJA Focus Overlay — Abejita Señaladora

> **AI agents talk. Now they can point.**

MIJA is a **visual guidance protocol** that lets AI agents highlight things on your screen — buttons, errors, windows, files — in real time. Transparent overlay. Click-through. Multi-monitor. Zero network.

```bash
pip install -r requirements.txt
python start_bee.bat
```

## What It Does

| Feature | Command |
|---|---|
| Highlight a region | `python main.py highlight <x> <y> <w> <h> green "PULSA AQUI" 15` |
| Find & highlight a window | `python main.py find "Brave"` |
| Visual template match | `python main.py match save_btn green 0.8 10` |
| Save a visual template | `python main.py save_template save_btn 100 200 80 40` |
| Clear overlay | `python main.py clear` |
| Multi-monitor calibration | `python main.py calibrate` |

## Why MIJA?

Agents are great at reasoning. Terrible at pointing. MIJA bridges that gap — it's the missing sense for AI-Human collaboration:

- **Zero Tokens Visual Memory**: Save screen regions as templates. Match them later by image, not by text description. Saves context window.
- **Click-Through Overlay**: The overlay is transparent to mouse/keyboard — you keep working, the agent keeps pointing.
- **Multi-Monitor DPI-Aware**: Virtual screen coordinates. Works across 1-4 monitors.
- **No Network, No Telemetry**: Everything runs locally. Your screen is yours.

## Quick Start

```bash
# 1. Install dependencies (~5 MB)
pip install -r requirements.txt

# 2. Optional: Install visual matching (~90 MB)
pip install -r requirements-vision.txt

# 3. Launch
python start_bee.bat

# 4. Try it
python main.py test
```

## Architecture

```
Agent → main.py → command.json → overlay.py → Screen
                         ↑
              matcher.py (visual memory, optional)
              vision.py  (window detection)
              selector.py (manual selection)
              resident_bee.py (system tray)
```

File-based IPC via atomic JSON writes. PID-based lifecycle. No race conditions.

## Protocol Colors

| Color | Meaning | Usage |
|---|---|---|
| Green | Confirmed | "Click here", "This is the file" |
| Yellow | Attention | "Look at this window", calibration |
| Red | Warning / Risk | "Don't touch this", "Error here" |
| Blue | Information | User-marked areas, context |

## For AI Agents

If you're an agent reading this, see [`AGENTS.md`](AGENTS.md) for the integration protocol. Any agent in the Colmena / IArtLabs Nexus ecosystem can use MIJA by calling `main.py` commands.

## Requirements

| Level | File | Size |
|---|---|---|
| Base | `requirements.txt` | ~5 MB |
| + Vision | `requirements-vision.txt` | ~90 MB (OpenCV + NumPy) |

---

**Built by IArtLabs — Colmena Ecosystem.**

*"Cero Humo, Total Evidencia."*
