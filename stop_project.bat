@echo off
setlocal
cd /d "%~dp0"

echo =====================================================================
echo                 STOPPING RAG QUEUE SERVICES
echo =====================================================================
echo.

echo [*] Stopping processes on port 8008...
powershell -NoProfile -Command "$conns = Get-NetTCPConnection -LocalPort 8008 -ErrorAction SilentlyContinue; if ($conns) { $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique; foreach ($id in $pids) { if ($id -gt 4) { Write-Host "Stopping PID $id on port 8008..."; Stop-Process -Id $id -Force -ErrorAction SilentlyContinue } } }"

echo.
echo [*] Terminating worker and API launcher windows...
taskkill /F /FI "WINDOWTITLE eq RAG Queue Worker*" /T >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq RAG Queue API Server*" /T >nul 2>&1

echo.
echo =====================================================================
echo                 ALL SERVICES HAVE BEEN STOPPED!
echo =====================================================================
echo.
ping 127.0.0.1 -n 2 >nul
endlocal
exit /b 0
