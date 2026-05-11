@echo off
title M.I.J.A Focus Overlay - Lanzador Maestro (HIBRIDO)
echo ==========================================
echo   M.I.J.A FOCUS OVERLAY - IArtLabs
echo   Iniciando Ecosistema Visual Hibrido...
echo ==========================================

:: Limpiar instancias previas de MIJA (selectivo por PID)
if exist overlay.pid (
    for /f "delims=" %%i in (overlay.pid) do taskkill /F /PID %%i >nul 2>&1
    del overlay.pid >nul 2>&1
)
if exist bee.pid (
    for /f "delims=" %%i in (bee.pid) do taskkill /F /PID %%i >nul 2>&1
    del bee.pid >nul 2>&1
)
:: Fallback: kill por titulo (multi-monitor wildcard)
powershell -Command "Get-Process | Where-Object {$_.MainWindowTitle -like 'MIJA_Focus_Overlay*'} | Stop-Process -Force" >nul 2>&1

:: Iniciar Motores
start /B python overlay.py
start /B python resident_bee.py
start /B python api.py

echo.
echo [SISTEMA ONLINE]
echo 1. Overlay Click-Through Activado.
echo 2. Abejita Residente en Barra de Tareas.
echo 3. API Bridge en puerto 8000 (Web-Ready).
echo.
echo Presiona cualquier tecla para apagar el sistema...
pause >nul

python main.py stop
echo Sistema Cerrado.
