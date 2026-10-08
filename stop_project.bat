@echo off
chcp 65001 >nul
title Stopping RAG Queue Services
cls

echo =====================================================================
echo                🛑  STOPPING RAG QUEUE SERVICES  🛑
echo =====================================================================
echo.

echo [*] Stopping processes on port 8008...

powershell -NoProfile -Command ^
    "$conns = Get-NetTCPConnection -LocalPort 8008 -ErrorAction SilentlyContinue; " ^
    "if ($conns) { " ^
    "    $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique; " ^
    "    foreach ($id in $pids) { " ^
    "        if ($id -gt 4) { " ^
    "            Write-Host \"Stopping PID $id on port 8008...\"; " ^
    "            Stop-Process -Id $id -Force -ErrorAction SilentlyContinue " ^
    "        } " ^
    "    } " ^
    "}"

echo.
echo [*] Terminating worker and API launcher windows...
taskkill /F /FI "WINDOWTITLE eq RAG Queue Worker*" /T >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq RAG Queue API Server*" /T >nul 2>&1

echo.
echo =====================================================================
echo                ✅  ALL SERVICES HAVE BEEN STOPPED!  ✅
echo =====================================================================
echo.
timeout /t 2 >nul
exit /b 0
