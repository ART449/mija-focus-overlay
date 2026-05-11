# Mini-Tutorial: MIJA Focus Overlay (Abejita Señaladora)

¡Bienvenido al sistema de guía visual de Colmena! Si no ves los recuadros o acabas de encender el sistema, sigue esta guía rápida de 1 minuto.

## 1. El Problema de "No se ve nada"
La mayoría de las veces ocurre por dos razones:
- **Multi-monitores**: El sistema no sabe en qué monitor estás mirando.
- **Ventanas Frontales**: Alguna ventana muy pesada está tapando el overlay (aunque es raro).

## 2. La Solución: Calibración
Si no ves a la Abejita, ejecuta este comando en tu terminal:

```powershell
python c:\BYFLOW\MIJA_FOCUS_OVERLAY\main.py calibrate
```

**¿Qué pasará?**
La Abejita volará por cada uno de tus monitores (Laptop, Monitor 2, Monitor 3, etc.) y pintará un cuadro amarillo grande en el centro de cada uno. 
- Si ves el cuadro en todos los monitores -> **¡Sincronizado!**
- Si solo lo ves en uno -> Reporta a la IA qué monitor falta.

## 3. Comandos Útiles para Humanos
- **Limpiar todo**: `python main.py clear` (Si te estorban los cuadros).
- **Buscar Ventana**: `python main.py find "Brave"` (Para ver si la Abejita encuentra tus apps).
- **Reiniciar Motor**: Si todo falla, cierra la terminal y corre `python overlay.py`.

## 4. Las Reglas de Oro
1. **La Abejita te sigue**: Si cambias de monitor tu ventana principal, avísale a la IA: *"Estoy en la pantalla de la laptop"*.
2. **Criterio IA**: La IA solo activará el overlay cuando sea estrictamente necesario para guiarte (Ley de Guía Visual).

---
**¡Listo para volar!**
*Firmado: El Agente Cartógrafo y la Abejita Señaladora.*
