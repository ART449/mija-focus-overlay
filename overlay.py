import tkinter as tk
import ctypes
import os
import json
import time

# Windows Constants
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x80000
WS_EX_TRANSPARENT = 0x20
WS_EX_TOPMOST = 0x8

def set_click_through(hwnd):
    """Sets the window to be click-through and always-on-top."""
    try:
        styles = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, styles | WS_EX_LAYERED | WS_EX_TRANSPARENT)
        ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002) # HWND_TOPMOST
    except Exception as e:
        print(f"Failed to set window styles: {e}")

class MIJAOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MIJA_Focus_Overlay")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "white")
        self.root.config(bg="white")
        
        # Full Screen
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        
        self.canvas = tk.Canvas(self.root, bg="white", highlightthickness=0, width=self.screen_width, height=self.screen_height)
        self.canvas.pack()
        
        # Initialize
        self.root.update()
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        if not hwnd: hwnd = self.root.winfo_id()
        set_click_through(hwnd)
        
        self.command_file = "command.json"
        self.last_mtime = 0
        self.pulse_val = 0
        self.current_box = None
        
        self.check_commands()
        self.animate()

    def draw_highlight(self, x, y, w, h, color="green", label=""):
        self.canvas.delete("all")
        self.current_box = {"x": x, "y": y, "w": w, "h": h, "color": color, "label": label}
        self.render_box()

    def render_box(self):
        if not self.current_box: return
        
        x, y, w, h = self.current_box["x"], self.current_box["y"], self.current_box["w"], self.current_box["h"]
        color = self.current_box["color"]
        label = self.current_box["label"]
        
        # Pulse effect
        p = self.pulse_val
        self.canvas.delete("box")
        self.canvas.create_rectangle(x-p, y-p, x+w+p, y+h+p, outline=color, width=3, tags="box")
        self.canvas.create_rectangle(x, y, x+w, y+h, outline=color, width=1, tags="box")
        
        if label:
            self.canvas.create_text(x, y-15, text=label.upper(), fill=color, anchor="nw", 
                                  font=("Segoe UI", 12, "bold"), tags="box")

    def animate(self):
        self.pulse_val = (self.pulse_val + 1) % 10
        self.render_box()
        self.root.after(100, self.animate)

    def check_commands(self):
        if os.path.exists(self.command_file):
            try:
                mtime = os.path.getmtime(self.command_file)
                if mtime > self.last_mtime:
                    self.last_mtime = mtime
                    with open(self.command_file, "r") as f:
                        data = json.load(f)
                        if data.get("action") == "highlight":
                            self.draw_highlight(data["x"], data["y"], data["w"], data["h"], 
                                               data.get("color", "green"), data.get("label", ""))
                        elif data.get("action") == "clear":
                            self.canvas.delete("all")
                            self.current_box = None
            except Exception as e:
                pass # Silently handle file contention
        self.root.after(200, self.check_commands)

if __name__ == "__main__":
    print("Abejita Señaladora: ONLINE")
    MIJAOverlay().root.mainloop()
