@echo off
title MTC Backend - Auto Restart
color 0A

:start
echo.
echo ============================================
echo   MTC Backend starting at %date% %time%
echo ============================================

:: Kill anything already on port 8000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING 2^>nul') do (
    echo   Killing stale process on port 8000 PID: %%a ...
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 1 /nobreak > nul

cd /d %~dp0backend

echo.
echo ============================================
echo   Checking python dependencies...
echo ============================================
python -m pip install -r requirements.txt

echo.
echo ============================================
echo   Starting FastAPI Server...
echo ============================================
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

echo.
echo ============================================
echo   Backend stopped! Restarting in 3 seconds...
echo   Press Ctrl+C to stop permanently.
echo ============================================
timeout /t 3 /nobreak > nul
goto start
