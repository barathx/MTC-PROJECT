@echo off
title MTC Verification System - Launcher
color 0E
echo ============================================
echo   MTC Verification System - Starting...
echo ============================================
echo.

:: ── Kill any old backend/frontend processes ──
echo [CLEANUP] Killing old processes on ports 8000 and 3000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING 2^>nul') do (
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000 ^| findstr LISTENING 2^>nul') do (
    taskkill /PID %%a /F >nul 2>&1
)
echo    Done.

:: ── Remove stale Next.js lock file ──
if exist "%~dp0frontend\.next\dev\lock" (
    echo [CLEANUP] Removing stale .next/dev/lock file...
    del /f /q "%~dp0frontend\.next\dev\lock" >nul 2>&1
    echo    Done.
)

timeout /t 2 /nobreak > nul

:: ── Start Backend ──
echo.
echo [1/2] Starting Backend (FastAPI) on port 8000...
start "MTC Backend" cmd /k "cd /d %~dp0 && run_backend.bat"

timeout /t 3 /nobreak > nul

:: ── Start Frontend ──
echo [2/2] Starting Frontend (Next.js) on port 3000...
start "MTC Frontend" cmd /k "cd /d %~dp0 && run_frontend.bat"

timeout /t 12 /nobreak > nul

:: ── Open browser ──
echo.
echo Opening browser...
start http://localhost:3000

echo.
echo ============================================
echo   Both servers are running!
echo.
echo   Frontend: http://localhost:3000
echo   Backend:  http://127.0.0.1:8000
echo   API Docs: http://127.0.0.1:8000/docs
echo.
echo   Servers auto-restart if they crash.
echo   To stop: close the server windows or
echo   press Ctrl+C inside them.
echo ============================================
echo.
echo You can close this launcher window safely.
pause
