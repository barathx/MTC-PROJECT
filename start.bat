@echo off
title MTC Verification System - Launcher
echo ============================================
echo   MTC Verification System - Starting...
echo ============================================
echo.

:: Start Backend with auto-restart
echo [1/2] Starting Backend (FastAPI) on port 8000...
start "MTC Backend" cmd /k "cd /d %~dp0backend && %~dp0run_backend.bat"

:: Wait a moment for backend to initialize
timeout /t 3 /nobreak > nul

:: Start Frontend with auto-restart
echo [2/2] Starting Frontend (Next.js) on port 3000...
start "MTC Frontend" cmd /k "cd /d %~dp0frontend && %~dp0run_frontend.bat"

:: Wait for frontend to start
timeout /t 5 /nobreak > nul

:: Open the app in default browser
echo.
echo Opening browser...
start http://localhost:3000

echo.
echo ============================================
echo   Both servers are running!
echo   Backend:  http://127.0.0.1:8000
echo   Frontend: http://localhost:3000
echo   API Docs: http://127.0.0.1:8000/docs
echo ============================================
echo.
echo Servers will AUTO-RESTART if they crash.
echo You can close this window safely.
pause
