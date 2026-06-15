@echo off
title Mirai Ray — Backend Server
cd /d "%~dp0"

echo ============================================
echo  MIRAI CORE — Starting Ray Backend
echo ============================================
echo.

:: Step 1: Check Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [FAIL] Python not found. Please install Python 3.10+
    pause
    exit /b 1
)
echo [OK] Python found: 
python --version

:: Step 2: Check Node.js (for opencode)
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [WARN] Node.js not found — opencode serve will not start
    echo [WARN] Install Node.js from https://nodejs.org/
) else (
    echo [OK] Node.js found:
    node --version
)

:: Step 3: Check opencode
where opencode >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [OK] opencode found: 
    opencode --version
) else (
    echo [FAIL] opencode not found. Install with: npm install -g opencode-ai
    pause
    exit /b 1
)

:: Step 4: Check virtual environment
if exist venv\Scripts\activate (
    echo [OK] Virtual environment found
    call venv\Scripts\activate
) else if exist .venv\Scripts\activate (
    echo [OK] Virtual environment found (.venv)
    call .venv\Scripts\activate
) else (
    echo [INFO] No venv found, using system Python
)

:: Step 5: Install Python dependencies
echo [INFO] Checking dependencies...
python -c "import uvicorn, fastapi, dotenv" 2>nul
if %ERRORLEVEL% neq 0 (
    echo [INFO] Installing dependencies...
    pip install -r mirai-core/requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo [FAIL] Failed to install dependencies
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed
) else (
    echo [OK] Dependencies satisfied
)

:: Step 6: Start opencode serve (background)
echo [INFO] Starting opencode serve on port 4096...
start "opencode-server" cmd /c "opencode serve --port 4096 --hostname 0.0.0.0 --cors *"
echo [OK] opencode server started

:: Step 7: Wait for opencode
echo [INFO] Waiting for opencode server...
:wait_opencode
timeout /t 2 /nobreak >nul
python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:4096/global/health')" 2>nul
if %ERRORLEVEL% neq 0 (
    echo [INFO] Still waiting...
    goto wait_opencode
)
echo [OK] opencode server ready

:: Step 8: Start FastAPI server
cd mirai-core
echo.
echo ============================================
echo  Starting Mirai Core on port 8765
echo ============================================
echo  AI Engine:  opencode serve (port 4096)
echo  API:        http://0.0.0.0:8765/
echo  Health:     http://127.0.0.1:8765/health
echo  Android:    http://10.0.2.2:8765/  (emulator)
echo  Press Ctrl+C to stop both servers
echo ============================================
echo.

python main.py

:: Cleanup on exit
echo [INFO] Stopping opencode server...
taskkill /f /fi "WINDOWTITLE eq opencode-server" >nul 2>nul

if %ERRORLEVEL% neq 0 (
    echo.
    echo [FAIL] Server exited with error code %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)
