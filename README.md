# M.I.J.A Focus Overlay (Abejita Señaladora)

Visual assistance system for identifying UI elements on screen.

## How to use

1. **Start Overlay**:
   ```bash
   python overlay.py
   ```
   (A transparent window will cover your screen. It is "click-through", so you can continue using your PC normally).

2. **Highlight an element**:
   ```bash
   python main.py highlight <x> <y> <w> <h> <color> <label>
   ```
   Example: `python main.py highlight 100 100 200 50 green "Boton Aceptar"`

3. **Find a window by title**:
   ```bash
   python main.py find "Notepad"
   ```

4. **Clear current highlights**:
   ```bash
   python main.py clear
   ```

5. **Stop Overlay**:
   ```bash
   python main.py stop
   ```

## Architecture
- `overlay.py`: The UI engine (Tkinter + Windows API).
- `vision.py`: Screen capture and window coordinate utilities.
- `main.py`: Command-line controller.
- `command.json`: Communication bridge.

## Project Goal
This is part of the **Abeja Señaladora** (Guide Bee) system to convert visual chaos into a navigable structure.
