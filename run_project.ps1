# RAG Queue System PowerShell Launcher
$Host.UI.RawUI.WindowTitle = "RAG Queue System Launcher"
Clear-Host

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "               RAG QUEUE SYSTEM LAUNCHER                             " -ForegroundColor Cyan
Write-Host "      Asynchronous RAG Pipeline with Redis Queue & Qdrant           " -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# 1. Ensure .env exists
if (-not (Test-Path ".env")) {
    Write-Host "[*] .env not found. Creating from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "[*] .env created successfully." -ForegroundColor Green
}

# 2. Check Docker Containers
Write-Host "[*] Checking Docker containers for Redis and Qdrant..." -ForegroundColor Yellow
$dockerRunning = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARNING] Docker Desktop is not running or not in PATH!" -ForegroundColor Red
    Write-Host "Please ensure Docker Desktop is started for Redis and Qdrant.`n" -ForegroundColor Red
} else {
    # Check/Start Redis
    $redisRunning = docker ps --format "{{.Names}}" | Select-String "redis"
    if (-not $redisRunning) {
        Write-Host "[*] Starting Redis container..." -ForegroundColor Yellow
        docker start redis-stack 2>$null
        if ($LASTEXITCODE -ne 0) {
            docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest 2>$null
        }
    }
    Write-Host "[OK] Redis is active on port 6379." -ForegroundColor Green

    # Check/Start Qdrant
    $qdrantRunning = docker ps --format "{{.Names}}" | Select-String "qdrant"
    if (-not $qdrantRunning) {
        Write-Host "[*] Starting Qdrant container..." -ForegroundColor Yellow
        docker start qdrant-db 2>$null
        if ($LASTEXITCODE -ne 0) {
            docker run -d --name qdrant-db -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest 2>$null
        }
    }
    Write-Host "[OK] Qdrant is active on port 6333." -ForegroundColor Green
}

# 3. Check Python
$pyVer = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Python not found on PATH! Please install Python 3.10+." -ForegroundColor Red
    Read-Host "Press Enter to exit..."
    exit 1
}

Write-Host "`n[*] Launching RQ Background Worker..." -ForegroundColor Cyan
Start-Process cmd -ArgumentList "/k", "cd /d `"$ScriptDir`" && python run_worker.py" -WindowStyle Normal

Start-Sleep -Seconds 2

Write-Host "[*] Launching FastAPI Web Server on http://localhost:8008 ..." -ForegroundColor Cyan
Start-Process cmd -ArgumentList "/k", "cd /d `"$ScriptDir`" && python main.py" -WindowStyle Normal

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "                ALL SERVICES ARE RUNNING!                            " -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "   API Server:       http://localhost:8008/" -ForegroundColor White
Write-Host "   Swagger Docs:     http://localhost:8008/docs" -ForegroundColor White
Write-Host "   Qdrant Dashboard: http://localhost:6333/dashboard" -ForegroundColor White
Write-Host "   Redis Broker:     localhost:6379" -ForegroundColor White
Write-Host "   RQ Worker:        Active in separate window" -ForegroundColor White
Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Yellow
Write-Host "   To STOP all services, run: .\stop_project.ps1 or stop_project.bat" -ForegroundColor Yellow
Write-Host "=====================================================================" -ForegroundColor Yellow
Write-Host ""

Start-Process "http://localhost:8008/docs"
