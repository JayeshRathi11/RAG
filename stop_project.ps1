# RAG Queue System PowerShell Stop Script
$Host.UI.RawUI.WindowTitle = "Stopping RAG Queue Services"
Clear-Host

Write-Host "=====================================================================" -ForegroundColor Yellow
Write-Host "               STOPPING RAG QUEUE SERVICES                           " -ForegroundColor Yellow
Write-Host "=====================================================================" -ForegroundColor Yellow
Write-Host ""

Write-Host "[*] Stopping processes on port 8008..." -ForegroundColor Cyan
$conns = Get-NetTCPConnection -LocalPort 8008 -ErrorAction SilentlyContinue
if ($conns) {
    $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($id in $pids) {
        if ($id -gt 4) {
            Write-Host "Stopping PID $id on port 8008..." -ForegroundColor Yellow
            Stop-Process -Id $id -Force -ErrorAction SilentlyContinue
        }
    }
}

Write-Host "[*] Terminating worker and API launcher windows..." -ForegroundColor Cyan
taskkill /F /FI "WINDOWTITLE eq RAG Queue Worker*" /T 2>$null | Out-Null
taskkill /F /FI "WINDOWTITLE eq RAG Queue API Server*" /T 2>$null | Out-Null

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "               ALL SERVICES HAVE BEEN STOPPED!                       " -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host ""
Start-Sleep -Seconds 1
