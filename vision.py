import win32gui
from PIL import ImageGrab
import os

def get_window_rect(window_title):
    """Returns the (x, y, w, h) of a window by its title."""
    try:
        hwnd = win32gui.FindWindow(None, window_title)
        if hwnd:
            rect = win32gui.GetWindowRect(hwnd)
            x, y, x2, y2 = rect
            return (x, y, x2 - x, y2 - y)
        return None
    except Exception as e:
        print(f"Window search failed: {e}")
        return None

def capture_screen(filename="screen_capture.png"):
    """Captures the entire screen and saves it to a file."""
    try:
        # all_screens=True to capture multi-monitor setups if needed
        screenshot = ImageGrab.grab(all_screens=True)
        screenshot.save(filename)
        return os.path.abspath(filename)
    except Exception as e:
        print(f"Capture failed: {e}")
        return None

if __name__ == "__main__":
    path = capture_screen()
    if path:
        print(f"Screenshot saved to: {path}")
