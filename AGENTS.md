# M.I.J.A Focus Overlay - Protocolo de Integración para Agentes (v1.0)

Este documento es una guía técnica obligatoria para cualquier agente del ecosistema **Colmena / IArtLabs Nexus** que requiera interactuar con la interfaz visual del usuario.

## 1. Arquitectura de Comunicación
El sistema utiliza un puente de comandos asíncrono basado en JSON.
- **Archivo de Control**: `c:\BYFLOW\MIJA_FOCUS_OVERLAY\command.json`
- **Controlador Maestro**: `main.py`

## 2. API de Comandos para Agentes
Cualquier agente externo debe usar `main.py` para interactuar. No se recomienda escribir directamente en el JSON para evitar condiciones de carrera.

### Resaltar Objetivo (Highlight)
**Uso**: Cuando necesites que el usuario mire un punto exacto.
```bash
python main.py highlight <x> <y> <w> <h> <color> <label> <duration>
```

### Memoria Visual (Templates)
**Uso**: Para reconocer elementos sin usar Vision AI (Cero tokens).
1. **Guardar**: `python main.py save_template <nombre> <x> <y> <w> <h>`
2. **Reconocer**: `python main.py match <nombre> <color?> <sensibilidad?> <duracion?>`
   - *Sensibilidad*: `0.8` por defecto (1.0 es exacto).
- **Parametros**:
  - `color`: `green` (confirmado), `red` (alerta/posible), `blue` (información).
  - `label`: Máximo 40 caracteres para legibilidad en la burbuja.
  - `duration`: Segundos que el highlight permanecerá activo (Recomendado: `15`).

### Localizar Ventana (Find)
**Uso**: Antes de señalar, localiza la ventana para obtener sus coordenadas absolutas.
```bash
python main.py find "Nombre de la Ventana"
```

## 3. Doctrina Operativa "Cero Humo"
Para garantizar la soberanía y seguridad del usuario, todo agente debe seguir estas reglas:
1. **Highlight Preventivo**: Antes de realizar cualquier acción en el navegador o sistema de archivos que requiera atención humana, se debe señalar el área de impacto.
2. **Confirmación de Duración**: Los agentes deben usar duraciones de al menos 10 segundos para dar tiempo de reacción al humano en entornos multi-monitor.
3. **Manejo de Errores**: Si un `highlight` devuelve error, el agente debe intentar una `calibrate` o solicitar al usuario que use el **Selector Manual** vía `resident_bee.py`.

## 4. Troubleshooting para Agentes
Si el sistema no responde:
1. Verificar proceso `python overlay.py` en ejecución.
2. Ejecutar `python main.py clear` para resetear el estado del canvas.

---
**Certificación**: IArtLabs Nexus Core - Protocolo de Guía Visual Soberana.
