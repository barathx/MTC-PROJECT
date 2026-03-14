@echo off
title MTC Frontend - Auto Restart
color 0B

:start
echo.
echo ============================================
echo   MTC Frontend starting at %date% %time%
echo ============================================

:: Kill anything already on port 3000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000 ^| findstr LISTENING 2^>nul') do (
    echo   Killing stale process on port 3000 PID: %%a ...
    taskkill /PID %%a /F >nul 2>&1
)

:: Remove stale Next.js lock file
if exist "%~dp0frontend\.next\dev\lock" (
    echo   Removing stale .next/dev/lock...
    del /f /q "%~dp0frontend\.next\dev\lock" >nul 2>&1
)
timeout /t 1 /nobreak > nul

cd /d %~dp0frontend

echo.
echo ============================================
echo   Checking node dependencies...
echo ============================================
if not exist node_modules\ (
    echo Installing dependencies...
    npm install
) else (
    echo Dependencies already installed.
)

echo.
echo ============================================
echo   Starting Next.js Server...
echo ============================================
npm run dev

echo.
echo ============================================
echo   Frontend stopped! Restarting in 3 seconds...
echo   Press Ctrl+C to stop permanently.
echo ============================================
timeout /t 3 /nobreak > nul
goto start
