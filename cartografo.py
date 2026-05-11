import json
import os
import win32gui
from vision import get_window_rect

class CartografoAgent:
    """
    Agente Cartógrafo: Responsable de mapear el espacio visual del usuario.
    Convierte descripciones semánticas en coordenadas exactas de pantalla.
    """
    def __init__(self):
        self.current_map = {}
        self.browser_offset = (0, 0) # Base coordinates of the browser window

    def mapear_ventanas(self):
        """Genera un mapa de todas las ventanas visibles actualmente."""
        windows = []
        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    rect = win32gui.GetWindowRect(hwnd)
                    x, y, x2, y2 = rect
                    windows.append({
                        "id": hwnd,
                        "title": title,
                        "rect": (x, y, x2 - x, y2 - y)
                    })
        win32gui.EnumWindows(callback, None)
        self.current_map["windows"] = windows
        return windows

    def localizar(self, query):
        """Busca la mejor coincidencia para una consulta en el mapa actual."""
        self.mapear_ventanas()
        query = query.lower()
        
        # Buscar coincidencias en títulos de ventanas
        for win in self.current_map["windows"]:
            if query in win["title"].lower():
                return win["rect"], win["title"]
        
        # Áreas estándar dinámicas
        if "barra de tareas" in query or "taskbar" in query:
             import win32api
             import win32con
             sw = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
             sh = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
             return (0, sh - 60, sw, 60), "Barra de Tareas"
        
        return None, None

if __name__ == "__main__":
    import sys
    carto = CartografoAgent()
    if len(sys.argv) > 1:
        q = " ".join(sys.argv[1:])
        rect, name = carto.localizar(q)
        if rect:
            print(json.dumps({"status": "FOUND", "target": name, "rect": rect}))
        else:
            print(json.dumps({"status": "NOT_FOUND"}))
    else:
        # Modo reporte de mapa
        mapa = carto.mapear_ventanas()
        print(f"Cartógrafo: He mapeado {len(mapa)} ventanas activas.")
