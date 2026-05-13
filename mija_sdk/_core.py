import json
import os
import subprocess
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN_PY = os.path.join(BASE_DIR, "main.py")
COMMAND_FILE = os.path.join(BASE_DIR, "command.json")
OVERLAY_PID = os.path.join(BASE_DIR, "overlay.pid")


def _ensure_overlay():
    if os.path.exists(OVERLAY_PID):
        try:
            with open(OVERLAY_PID) as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)
            return True
        except (OSError, ValueError):
            pass
    proc = subprocess.Popen(
        ["python", os.path.join(BASE_DIR, "overlay.py")],
        cwd=BASE_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(2)
    return proc.poll() is None


def _run(*args):
    cmd = ["python", MAIN_PY] + list(args)
    result = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip()


def highlight(x, y, w, h, color="green", label="FOCUS", duration=5.0):
    _ensure_overlay()
    return _run("highlight", str(x), str(y), str(w), str(h), color, label, str(duration))


def clear():
    return _run("clear")


def find(window_title):
    return _run("find", window_title)


def calibrate():
    return _run("calibrate")


def save_template(name, x, y, w, h):
    return _run("save_template", name, str(x), str(y), str(w), str(h))


def match(name, threshold=0.8, color="green", duration=5.0):
    return _run("match", name, color, str(threshold), str(duration))


def status():
    return {
        "overlay": os.path.exists(OVERLAY_PID),
        "base_dir": BASE_DIR,
    }


def stop():
    return _run("stop")


def _cli_main():
    import sys
    args = sys.argv[1:]
    if not args:
        print("MIJA Focus Overlay SDK v1.4")
        print("  mija highlight <x> <y> <w> <h> [color] [label] [duration]")
        print("  mija clear")
        print("  mija find <window_title>")
        print("  mija match <template> [threshold] [color] [duration]")
        print("  mija save <name> <x> <y> <w> <h>")
        print("  mija calibrate")
        print("  mija status")
        print("  mija mcp")
        return

    cmd = args[0].lower()
    if cmd == "highlight" and len(args) >= 5:
        out, _ = highlight(int(args[1]), int(args[2]), int(args[3]), int(args[4]),
                           args[5] if len(args) > 5 else "green",
                           args[6] if len(args) > 6 else "FOCUS",
                           float(args[7]) if len(args) > 7 else 5.0)
        print(out)
    elif cmd == "clear":
        out, _ = clear(); print(out)
    elif cmd == "find" and len(args) >= 2:
        out, _ = find(" ".join(args[1:])); print(out)
    elif cmd == "match" and len(args) >= 2:
        out, _ = match(args[1], float(args[2]) if len(args) > 2 else 0.8,
                       args[3] if len(args) > 3 else "green",
                       float(args[4]) if len(args) > 4 else 5.0)
        print(out)
    elif cmd == "save" and len(args) >= 6:
        out, _ = save_template(args[1], int(args[2]), int(args[3]), int(args[4]), int(args[5]))
        print(out)
    elif cmd == "calibrate":
        out, _ = calibrate(); print(out)
    elif cmd == "status":
        print(json.dumps(status(), indent=2))
    elif cmd == "mcp":
        from mija_sdk.mcp_server import main as mcp_main
        mcp_main()
    else:
        print(f"Unknown command: {cmd}")
