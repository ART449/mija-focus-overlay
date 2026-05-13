"""
CrewAI Tool wrappers for MIJA Focus Overlay.

Usage:
    from mija_sdk.crewai import create_mija_tools

    tools = create_mija_tools()
"""

from crewai.tools import tool
from mija_sdk._core import highlight, clear, find, match, save_template


def create_mija_tools():
    @tool("mija_highlight")
    def _highlight(x: int, y: int, w: int, h: int, color: str = "green", label: str = "FOCUS", duration: float = 5.0) -> str:
        """Draw a colored rectangle on the user's screen. Use to point at UI elements, buttons, or errors.
        Colors: green=confirmed, red=error, yellow=attention, blue=info."""
        out, _ = highlight(x, y, w, h, color, label, duration)
        return out

    @tool("mija_clear")
    def _clear() -> str:
        """Clear all MIJA overlays from the screen."""
        out, _ = clear()
        return out

    @tool("mija_find_window")
    def _find(window_title: str) -> str:
        """Find and highlight a window by its exact title."""
        out, _ = find(window_title)
        return out

    @tool("mija_match_template")
    def _match(name: str, threshold: float = 0.8, color: str = "green", duration: float = 5.0) -> str:
        """Find a saved visual template on screen and highlight it."""
        out, _ = match(name, threshold, color, duration)
        return out

    @tool("mija_save_template")
    def _save(name: str, x: int, y: int, w: int, h: int) -> str:
        """Save a screen region as a named template for future visual matching."""
        out, _ = save_template(name, x, y, w, h)
        return out

    return [_highlight, _clear, _find, _match, _save]
