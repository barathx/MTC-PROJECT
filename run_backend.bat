@echo off
title MTC Backend - Auto Restart
color 0A

:start
echo ============================================
echo   MTC Backend starting at %date% %time%
echo ============================================
echo.

cd /d %~dp0backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

echo.
echo ============================================
echo   Backend stopped! Restarting in 3 seconds...
echo   Press Ctrl+C to stop permanently.
echo ============================================
echo.
timeout /t 3 /nobreak > nul
goto start
