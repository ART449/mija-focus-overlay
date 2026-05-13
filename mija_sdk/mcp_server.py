"""
MCP Server for MIJA Focus Overlay.
Provides tools to AI assistants via the Model Context Protocol.

Auto-discovery: Claude Desktop and OpenCode detect this server automatically
when configured in their MCP settings.

Run:
    python -m mija_sdk.mcp_server

Or configure in ~/.config/claude/mcp.json:
    {"mcpServers": {"mija": {"command": "python", "args": ["-m", "mija_sdk.mcp_server"]}}}
"""

import json
import sys
from mija_sdk._core import highlight, clear, find, match, save_template, calibrate, status

HANDLERS = {
    "tools/list": lambda _: {
        "tools": [
            {
                "name": "mija_highlight",
                "description": "Draw a colored rectangle on the user's Windows screen to point at an area. Use to guide the user visually. Colors: green=confirmed/safe, red=warning/error, yellow=attention, blue=info.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "x": {"type": "integer", "description": "X coordinate"},
                        "y": {"type": "integer", "description": "Y coordinate"},
                        "w": {"type": "integer", "description": "Width"},
                        "h": {"type": "integer", "description": "Height"},
                        "color": {"type": "string", "enum": ["green", "red", "yellow", "blue"], "default": "green"},
                        "label": {"type": "string", "default": "FOCUS", "description": "Label text, max 40 chars"},
                        "duration": {"type": "number", "default": 5.0, "description": "Seconds to display"},
                    },
                    "required": ["x", "y", "w", "h"],
                },
            },
            {
                "name": "mija_clear",
                "description": "Clear all MIJA overlays from the screen.",
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "mija_find_window",
                "description": "Find and highlight a window by its title.",
                "inputSchema": {
                    "type": "object",
                    "properties": {"window_title": {"type": "string"}},
                    "required": ["window_title"],
                },
            },
            {
                "name": "mija_match_template",
                "description": "Find a saved visual template (PNG) on screen and highlight it.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "threshold": {"type": "number", "default": 0.8},
                        "color": {"type": "string", "default": "green"},
                        "duration": {"type": "number", "default": 5.0},
                    },
                    "required": ["name"],
                },
            },
            {
                "name": "mija_save_template",
                "description": "Save a screen region as a visual template for future matching.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "x": {"type": "integer"}, "y": {"type": "integer"},
                        "w": {"type": "integer"}, "h": {"type": "integer"},
                    },
                    "required": ["name", "x", "y", "w", "h"],
                },
            },
            {
                "name": "mija_calibrate",
                "description": "Calibrate multi-monitor setup — shows a rectangle on each monitor.",
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "mija_status",
                "description": "Check if the MIJA overlay is running.",
                "inputSchema": {"type": "object", "properties": {}},
            },
        ]
    },
    "tools/call": lambda req: _dispatch(req["name"], req.get("arguments", {})),
}


def _dispatch(name, args):
    try:
        if name == "mija_highlight":
            out, _ = highlight(args["x"], args["y"], args["w"], args["h"], args.get("color", "green"), args.get("label", "FOCUS"), args.get("duration", 5.0))
        elif name == "mija_clear":
            out, _ = clear()
        elif name == "mija_find_window":
            out, _ = find(args["window_title"])
        elif name == "mija_match_template":
            out, _ = match(args["name"], args.get("threshold", 0.8), args.get("color", "green"), args.get("duration", 5.0))
        elif name == "mija_save_template":
            out, _ = save_template(args["name"], args["x"], args["y"], args["w"], args["h"])
        elif name == "mija_calibrate":
            out, _ = calibrate()
        elif name == "mija_status":
            out = json.dumps(status())
        else:
            return _error(f"Unknown tool: {name}")
        return {"content": [{"type": "text", "text": out}]}
    except Exception as e:
        return _error(str(e))


def _error(msg):
    return {"content": [{"type": "text", "text": f"ERROR: {msg}"}], "isError": True}


def main():
    print("MIJA MCP Server STARTED", file=sys.stderr, flush=True)
    for line in sys.stdin:
        try:
            req = json.loads(line.strip())
            method = req.get("method", "")
            rid = req.get("id")
            handler = HANDLERS.get(method)
            if handler:
                result = handler(req.get("params", {}))
                _send(rid, result)
            elif method == "initialize":
                _send(rid, {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "mija-overlay", "version": "1.4.0"},
                })
            else:
                _send(rid, {})
        except Exception as e:
            _send(req.get("id"), {"error": str(e)})


def _send(rid, result):
    msg = {"jsonrpc": "2.0", "id": rid, "result": result}
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


if __name__ == "__main__":
    main()
