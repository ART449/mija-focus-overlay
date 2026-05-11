import os
from PIL import ImageGrab

def find_template_on_screen(template_name, threshold=0.8):
    """
    Busca una imagen de plantilla en la pantalla actual.
    Lazy imports de OpenCV/Numpy para evitar crashes si no están instalados.
    """
    try:
        import cv2
        import numpy as np
    except ImportError:
        print("ERROR: OpenCV y Numpy no están instalados. Ejecuta 'pip install opencv-python numpy'")
        return None

    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_dir, "templates", template_name)
    
    if not os.path.exists(template_path):
        print(f"ERROR: No existe la plantilla {template_name}")
        return None

    # Captura de pantalla actual
    screenshot = np.array(ImageGrab.grab())
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
    
    # Cargar plantilla
    template = cv2.imread(template_path, 0)
    if template is None:
        print(f"ERROR: No se pudo leer la imagen {template_name}")
        return None
        
    w, h = template.shape[::-1]
    
    # Matcher de OpenCV
    res = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    if max_val >= threshold:
        return (max_loc[0], max_loc[1], w, h)
    else:
        return None

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        res = find_template_on_screen(sys.argv[1])
        if res: print(f"FOUND: {res}")
        else: print("NOT_FOUND")
