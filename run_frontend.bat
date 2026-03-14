@echo off
title MTC Frontend - Auto Restart
color 0B

:start
echo ============================================
echo   MTC Frontend starting at %date% %time%
echo ============================================
echo.

cd /d %~dp0frontend
npm run dev

echo.
echo ============================================
echo   Frontend stopped! Restarting in 3 seconds...
echo   Press Ctrl+C to stop permanently.
echo ============================================
echo.
timeout /t 3 /nobreak > nul
goto start
