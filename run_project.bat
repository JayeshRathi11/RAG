@echo off
setlocal
cd /d "%~dp0"

echo =====================================================================
echo                 RAG QUEUE SYSTEM LAUNCHER
echo      Asynchronous RAG Pipeline with Redis Queue and Qdrant
echo =====================================================================
echo.

REM 1. Ensure .env exists
if not exist ".env" (
    echo [*] .env not found. Creating from .env.example...
    copy ".env.example" ".env" >nul
    echo [*] .env created successfully.
)

REM 2. Check Docker Containers
echo [*] Checking Docker containers for Redis and Qdrant...
docker info >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Docker is not running or not in PATH!
    echo Please make sure Docker Desktop is running for Redis and Qdrant.
) else (
    docker ps --format "{{.Names}}" | findstr /I "redis" >nul 2>&1
    if errorlevel 1 (
        echo [*] Starting Redis container...
        docker start redis-stack >nul 2>&1
        if errorlevel 1 (
            docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest >nul 2>&1
        )
    )
    echo [OK] Redis is active on port 6379.

    docker ps --format "{{.Names}}" | findstr /I "qdrant" >nul 2>&1
    if errorlevel 1 (
        echo [*] Starting Qdrant container...
        docker start qdrant-db >nul 2>&1
        if errorlevel 1 (
            docker run -d --name qdrant-db -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest >nul 2>&1
        )
    )
    echo [OK] Qdrant is active on port 6333.
)

REM 3. Check Python
echo [*] Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found on PATH! Please install Python.
    pause
    exit /b 1
)

echo.
echo [*] Launching RQ Background Worker...
start "RAG Queue Worker" cmd /k "cd /d "%~dp0" ^&^& python run_worker.py"

ping 127.0.0.1 -n 3 >nul

echo [*] Launching FastAPI Web Server on http://localhost:8008 ...
start "RAG Queue API Server" cmd /k "cd /d "%~dp0" ^&^& python main.py"

ping 127.0.0.1 -n 3 >nul

echo.
echo =====================================================================
echo                 ALL SERVICES ARE RUNNING!
echo =====================================================================
echo.
echo   API Server:       http://localhost:8008/
echo   Swagger Docs:     http://localhost:8008/docs
echo   Qdrant Dashboard: http://localhost:6333/dashboard
echo   Redis Broker:     localhost:6379
echo   RQ Worker:        Active in separate window
echo.
echo =====================================================================
echo   To STOP all services, run: stop_project.bat
echo =====================================================================
echo.

start http://localhost:8008/docs

endlocal
exit /b 0
