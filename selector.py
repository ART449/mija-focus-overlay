import tkinter as tk
import json
import sys

class AreaSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MIJA Selector: Arrastra y delimita el área")
        self.root.attributes("-alpha", 0.5) # Semi-transparente
        self.root.attributes("-topmost", True)
        
        # Tamaño inicial estándar
        self.root.geometry("400x300+500+500")
        
        # Botón para confirmar
        self.btn = tk.Button(self.root, text="CONFIRMAR ÁREA", command=self.confirmar, bg="green", fg="white", font=("Arial", 12, "bold"))
        self.btn.pack(side="bottom", fill="x")
        
        self.label = tk.Label(self.root, text="Mueve y estira esta ventana\nsobre el área que quieres marcar", bg="black", fg="white")
        self.label.pack(expand=True, fill="both")
        
        self.root.mainloop()

    def confirmar(self):
        # Obtener coordenadas finales
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        
        result = {"x": x, "y": y, "w": w, "h": h}
        with open("selection.json", "w") as f:
            json.dump(result, f)
        
        print(f"SELECCIÓN GUARDADA: {result}")
        self.root.destroy()

if __name__ == "__main__":
    AreaSelector()
