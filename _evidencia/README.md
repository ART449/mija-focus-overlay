# Evidencia — MIJA Focus Overlay

Esta carpeta guarda **videos y capturas históricas** del overlay. Los archivos binarios viven aquí en disco pero **no** se commitean a git (ver `.gitignore`). Solo este README va al repo, apuntando al qué y al cuándo.

## first_light_2026-05-12_0751.mp4 — 291 MB

**Captura de ArT (07:51:31, 2026-05-12)** — el momento en que MIJA dejó de ser una ventana blanca opaca y pasó a ser un overlay transparente real.

Cambios técnicos que provocaron este "first light" (commit `dcfd61a`):
- Chroma key magenta `#ff00ff` en lugar de `white` (Win11 compositor)
- HWND vía `winfo_id()` + `GetParent()` walk (no `FindWindow`)
- Layered window vía ctypes directo
- `transient(self.root)` para sacar las ventanas del taskbar
- `ShowWindow(SW_HIDE → SW_SHOWNA)` cycle para refresh

Es la primera prueba grabada del overlay funcionando como debe.

**Ground truth**: si alguien duda más adelante "¿de verdad jaló MIJA?", aquí está el video. Antes y después del fix, el overlay aparecía como ventana blanca sólida. Después, transparente click-through con grid + label.

## Política de evidencia

- Los videos pueden vivir aquí o subirse a `Google Drive › IArtLabs › ByFlow_Production › MIJA`
- No hace falta versionarlos en git (pesan, y el repo se contamina)
- Pero **sí versionamos este README** con la lista de qué hay y por qué importa
