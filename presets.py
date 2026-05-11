import json

# Plantillas estándar de UI para la Abejita
# Evita el "puro código" y usa tamaños consistentes
PRESETS = {
    "btn": {"w": 120, "h": 45},
    "input": {"w": 350, "h": 40},
    "window": {"w": 800, "h": 600},
    "tiny": {"w": 50, "h": 50},
    "icon": {"w": 64, "h": 64},
    "sidebar": {"w": 250, "h": 1080},
    "header": {"w": 1920, "h": 80}
}

def get_preset_size(name):
    return PRESETS.get(name, {"w": 200, "h": 200})
