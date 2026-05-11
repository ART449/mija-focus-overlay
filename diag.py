import win32gui
import win32api
import win32con

def diag():
    print("--- MONITOR DIAGNOSTICS ---")
    monitors = win32api.EnumDisplayMonitors()
    for i, m in enumerate(monitors):
        print(f"Monitor {i+1}: {m[2]}")
    
    print("\n--- WINDOW SEARCH ---")
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "Brave" in title or "Google Cloud" in title:
                rect = win32gui.GetWindowRect(hwnd)
                windows.append((title, rect))
    
    windows = []
    win32gui.EnumWindows(callback, windows)
    for title, rect in windows:
        print(f"WINDOW: '{title}' at {rect}")

if __name__ == "__main__":
    diag()
