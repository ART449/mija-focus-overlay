import win32gui

def callback(hwnd, extra):
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd)
        if title:
            print(f"[{hwnd}] {title}")

print("Listing visible windows:")
win32gui.EnumWindows(callback, None)
