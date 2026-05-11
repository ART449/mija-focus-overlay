---
name: mija-focus-overlay
description: Controla la Abejita Señaladora para resaltar elementos visuales en la pantalla del usuario (Windows). Permite marcar botones, errores o ventanas con cuadros de colores y etiquetas. BASE/CENTRO/ACCION/VEREDICTO.
---

# MIJA Focus Overlay — Abejita Señaladora

Esta skill permite a los agentes Colmena guiar visualmente al usuario marcando áreas de interés en su propia pantalla (Windows). Convierte el caos visual en una estructura guiada mediante una capa de overlay transparente.

## Triggers

- "señala el botón de X" / "donde está Y"
- "marca el error en rojo" / "ilumina la ventana de Z"
- "limpia la pantalla" / "quita el cuadro"
- "dame foco en <coordenadas>"

## Mandato Supremo: Ley de Guía Visual
**SIEMPRE** que el agente requiera que el usuario realice una acción manual, quiera mostrar un resultado específico, o el usuario pregunte "¿dónde está?", se **DEBE** activar el overlay automáticamente. No es opcional; es la forma en que la IA y el Humano coordinan su atención.

## Roles (Colmena)

- **Agente Cartógrafo**: Escanea el espacio visual, identifica ventanas y regiones. Genera el "Mapa de Coordenadas".
- **Abejita Señaladora**: Recibe coordenadas del Cartógrafo y proyecta el overlay visual en la pantalla.

## Protocolo operativo (Trilineal)

```text
BASE: El Cartógrafo escanea la UI (ventanas, botones, landmarks).
CENTRO: Se define el target visual y el nivel de riesgo (Rojo/Verde).
ACCION: La Abejita proyecta el highlight con el label correspondiente.
VEREDICTO: READY si el foco visual guía al humano al objetivo.
```

## Componentes

- **Path Base**: `c:\BYFLOW\MIJA_FOCUS_OVERLAY`
- **Motor**: `overlay.py` (Debe estar corriendo en background)
- **Controlador**: `main.py`

## Comandos de Ejecución

### 1. Asegurar que el motor esté vivo
Si no aparece el recuadro, reiniciar el motor:
```powershell
python c:\BYFLOW\MIJA_FOCUS_OVERLAY\overlay.py
```

### 2. Resaltar Elemento
```powershell
python c:\BYFLOW\MIJA_FOCUS_OVERLAY\main.py highlight <x> <y> <w> <h> <color> "<etiqueta>" <duracion_segundos>
```
*Ejemplo: `python main.py highlight 100 100 200 50 green "PULSA AQUÍ" 15`*

### 3. Encontrar y Resaltar Ventana
```powershell
python c:\BYFLOW\MIJA_FOCUS_OVERLAY\main.py find "<Titulo de la Ventana>"
```

### 4. Limpiar Overlay
```powershell
python c:\BYFLOW\MIJA_FOCUS_OVERLAY\main.py clear
```

### 5. Calibración (Multi-Monitor)
Si el usuario no ve el highlight, forzar calibración:
```powershell
python c:\BYFLOW\MIJA_FOCUS_OVERLAY\main.py calibrate
```

### 6. Memoria Visual (Reconocimiento Local)
Para no gastar tokens, usar plantillas guardadas:
- **Guardar**: `python main.py save_template "mi_logo" 10 10 50 50`
- **Buscar**: `python main.py match "mi_logo" green 0.8 15`

### 7. Botón de Asistencia Humana (Resident Bee)
Para permitir que el usuario marque áreas manualmente en cualquier momento:
```powershell
python c:\BYFLOW\MIJA_FOCUS_OVERLAY\resident_bee.py
```
Aparecerá un botón `🐝` en la barra de tareas. Al hacer clic, lanza el `selector.py`.

Referencia completa: `c:\BYFLOW\MIJA_FOCUS_OVERLAY\TUTORIAL.md`

## Guía de Colores

| Color | Significado | Uso Típico |
|---|---|---|
| **green** | Acción segura | "Haz clic aquí", "Este es el archivo". |
| **yellow** | Informativo / Revisar | "Mira esta ventana", "Aquí está el manual". |
| **red** | Riesgo / Error | "No toques esto", "Aquí falló el proceso". |

## Integración Web (A11y-Focus)

Cuando el target es una página web (Brave/Chrome):
1.  Usar la skill `accessibility-tree` para mapear los elementos interactivos.
2.  Obtener el `boundingBox` del elemento deseado vía `browser_subagent`.
3.  Sumar el offset de la ventana del navegador (obtenido por el Cartógrafo) a las coordenadas del elemento.
4.  Proyectar el highlight.

## Anti-Humo
- Si las coordenadas fallan debido a DPI o multi-monitor, usar `python c:\BYFLOW\MIJA_FOCUS_OVERLAY\vision.py` para re-calibrar vía captura.
- Siempre confirmar con el usuario si el highlight es visible.
