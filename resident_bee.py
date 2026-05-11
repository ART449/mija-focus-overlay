import tkinter as tk
import subprocess
import os

class ResidentBee:
    def __init__(self):
        # GUARDAR PID PARA CIERRE SELECTIVO
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.pid_file = os.path.join(self.base_dir, "bee.pid")
        with open(self.pid_file, "w") as f:
            f.write(str(os.getpid()))

        self.root = tk.Tk()
        self.root.title("MIJA_Bee_Button")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.7) # SEMI-TRANSPARENTE
        
        # Posicionar exactamente en la barra de tareas (esquina inferior derecha)
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        # Tamaño más pequeño para que quepa en la barra (32x32)
        self.root.geometry(f"32x32+{screen_w - 240}+{screen_h - 40}")
        
        self.root.config(bg="yellow")
        
        # Icono de abeja más compacto
        self.btn = tk.Button(self.root, text="🐝", font=("Arial", 14), 
                             command=self.launch_selector, bg="yellow", relief="flat")
        self.btn.pack(expand=True, fill="both")
        
        # Hacerla arrastrable (por si molesta)
        self.btn.bind("<B1-Motion>", self.drag)
        self.x = 0
        self.y = 0
        self.btn.bind("<Button-1>", self.save_pos)

        print("Abejita Guía Residente: ONLINE")
        self.root.mainloop()

    def save_pos(self, event):
        self.x = event.x
        self.y = event.y

    def drag(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def launch_selector(self):
        # Lanzar el selector en un proceso separado usando rutas absolutas
        selector_path = os.path.join(self.base_dir, "selector.py")
        subprocess.Popen(["python", selector_path], cwd=self.base_dir)

if __name__ == "__main__":
    ResidentBee()
