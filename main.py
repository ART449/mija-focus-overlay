import sys
import json
import os
from vision import capture_screen

COMMAND_FILE = "command.json"

def send_command(data):
    """Writes a command to the JSON file for the overlay to read."""
    with open(COMMAND_FILE, "w") as f:
        json.dump(data, f)

def main():
    if len(sys.argv) < 2:
        print("M.I.J.A Focus Controller")
        print("Usage:")
        print("  python main.py highlight <x> <y> <w> <h> [color] [label]")
        print("  python main.py clear")
        print("  python main.py capture")
        print("  python main.py test")
        return

    cmd = sys.argv[1].lower()
    
    if cmd == "highlight":
        if len(sys.argv) < 6:
            print("Error: Missing coordinates. (x y w h)")
            return
        data = {
            "action": "highlight",
            "x": int(sys.argv[2]),
            "y": int(sys.argv[3]),
            "w": int(sys.argv[4]),
            "h": int(sys.argv[5]),
            "color": sys.argv[6] if len(sys.argv) > 6 else "green",
            "label": sys.argv[7] if len(sys.argv) > 7 else "FOCUS"
        }
        send_command(data)
        print(f"SENT: Highlight at ({data['x']}, {data['y']}) Color: {data['color']}")

    elif cmd == "clear":
        send_command({"action": "clear"})
        print("SENT: Clear Overlay")

    elif cmd == "capture":
        path = capture_screen()
        print(f"SCREENSHOT: {path}")

    elif cmd == "test":
        # Simulate a sequence
        print("Running Test Sequence...")
        import time
        send_command({"action": "highlight", "x": 100, "y": 100, "w": 300, "h": 100, "color": "green", "label": "TEST_VERDE"})
        time.sleep(2)
        send_command({"action": "highlight", "x": 500, "y": 300, "w": 200, "h": 200, "color": "red", "label": "TEST_ROJO"})
        time.sleep(2)
        send_command({"action": "clear"})
        print("Test Complete.")

    elif cmd == "find":
        if len(sys.argv) < 3:
            print("Usage: python main.py find <Window Title>")
            return
        from vision import get_window_rect
        title = " ".join(sys.argv[2:])
        rect = get_window_rect(title)
        if rect:
            x, y, w, h = rect
            send_command({"action": "highlight", "x": x, "y": y, "w": w, "h": h, "color": "yellow", "label": title})
            print(f"FOUND: {title} at {rect}")
        else:
            print(f"NOT FOUND: {title}")

    elif cmd == "stop":
        print("Stopping Overlay...")
        os.system('taskkill /F /FI "WINDOWTITLE eq MIJA_Focus_Overlay" >nul 2>&1')
        if os.path.exists(COMMAND_FILE):
            os.remove(COMMAND_FILE)
        print("Overlay Stopped.")

if __name__ == "__main__":
    main()
