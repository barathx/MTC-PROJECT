@echo off
title MTC - Stopping Servers
color 0C
echo ============================================
echo   Stopping all MTC servers...
echo ============================================
echo.

:: Kill backend on port 8000
echo Stopping Backend (port 8000)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING 2^>nul') do (
    taskkill /PID %%a /F >nul 2>&1
)

:: Kill frontend on port 3000
echo Stopping Frontend (port 3000)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000 ^| findstr LISTENING 2^>nul') do (
    taskkill /PID %%a /F >nul 2>&1
)

:: Kill any node processes from Next.js
taskkill /IM node.exe /F >nul 2>&1

:: Remove lock file
if exist "%~dp0frontend\.next\dev\lock" (
    del /f /q "%~dp0frontend\.next\dev\lock" >nul 2>&1
)

echo.
echo ============================================
echo   All servers stopped. Ports cleared.
echo ============================================
timeout /t 3 /nobreak > nul
