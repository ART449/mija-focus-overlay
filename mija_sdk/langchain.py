"""
LangChain Tool wrappers for MIJA Focus Overlay.
Agents can use these tools to visually guide the user.

Usage:
    from mija_sdk.langchain import MIJAHighlightTool, MIJAClearTool

    tools = [MIJAHighlightTool(), MIJAClearTool(), MIJAFindTool()]
"""

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional
from mija_sdk._core import highlight, clear, find, match


class HighlightInput(BaseModel):
    x: int = Field(description="X coordinate on screen")
    y: int = Field(description="Y coordinate on screen")
    w: int = Field(description="Width of the highlight rectangle")
    h: int = Field(description="Height of the highlight rectangle")
    color: str = Field(default="green", description="Color: green, red, yellow, blue")
    label: str = Field(default="FOCUS", description="Label text, max 40 chars")
    duration: float = Field(default=5.0, description="Duration in seconds")


class MIJAHighlightTool(BaseTool):
    name: str = "mija_highlight"
    description: str = (
        "Draw a colored rectangle on the user's screen to point at something. "
        "Use this whenever the user needs to see where to click or what to look at. "
        "Colors: green=confirmed, red=warning/error, yellow=attention, blue=info."
    )
    args_schema: type = HighlightInput

    def _run(self, x: int, y: int, w: int, h: int, color: str = "green", label: str = "FOCUS", duration: float = 5.0) -> str:
        out, _ = highlight(x, y, w, h, color, label, duration)
        return out


class MIJAClearTool(BaseTool):
    name: str = "mija_clear"
    description: str = "Clear all MIJA overlays from the user's screen."

    def _run(self) -> str:
        out, _ = clear()
        return out


class MIJAFindTool(BaseTool):
    name: str = "mija_find_window"
    description: str = (
        "Find and highlight a window by its title. "
        "Use this to point the user to a specific application window."
    )

    def _run(self, window_title: str) -> str:
        out, _ = find(window_title)
        return out


class MIJAMatchTool(BaseTool):
    name: str = "mija_match_template"
    description: str = (
        "Find a saved visual template (PNG) on screen and highlight it. "
        "Use this for pre-registered UI elements. Saves tokens vs describing coordinates."
    )

    def _run(self, template_name: str, threshold: float = 0.8, color: str = "green", duration: float = 5.0) -> str:
        out, _ = match(template_name, threshold, color, duration)
        return out
