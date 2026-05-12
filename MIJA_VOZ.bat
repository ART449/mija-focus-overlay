@echo off
title MIJA Voz - Asistente Visual IArtLabs
color 0E
cd /D "C:\BYFLOW\MIJA_FOCUS_OVERLAY"

echo ===============================================
echo   M.I.J.A VOZ - IArtLabs
echo   Apunta y hace click por ti, sin tocar nada
echo ===============================================
echo.

REM ─── 1. Levantar overlay si no esta corriendo ────────────────────────
if not exist overlay.pid (
    echo [1/3] Iniciando overlay transparente...
    start /B "" pythonw overlay.py
    timeout /t 2 /nobreak >nul
) else (
    echo [1/3] Overlay ya activo.
)

REM ─── 2. Levantar API si el puerto 8000 esta libre ────────────────────
powershell -NoProfile -Command "if ((Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue).Count -eq 0) { exit 1 } else { exit 0 }"
if errorlevel 1 (
    echo [2/3] Iniciando API en puerto 8000...
    start /B "" pythonw api.py
    timeout /t 3 /nobreak >nul
) else (
    echo [2/3] API ya activa.
)

REM ─── 3. Abrir Edge en modo app (ventana nativa, sin browser chrome) ──
echo [3/3] Abriendo ventana MIJA Voz en Edge...
echo.
echo  TIP: si pide permiso de microfono, dale PERMITIR
echo       (necesario para que te escuche)
echo.

start "" msedge --app=http://localhost:8000/voice --new-window

echo.
echo Listo. La ventana se abre en unos segundos.
echo Si Edge no abre, copia esta URL en cualquier navegador:
echo   http://localhost:8000/voice
echo.
timeout /t 5 /nobreak >nul
exit
