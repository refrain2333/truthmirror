@echo off
chcp 65001 >nul
title Truth Mirror - Backend Server
color 0B
echo ====================================
echo    Truth Mirror - Backend Server
echo ====================================
echo.

cd /d "%~dp0backend"

echo Checking backend directory...
if not exist "run.py" (
    echo [ERROR] run.py not found
    echo Please ensure you are running this script in the correct directory
    pause
    exit /b 1
)

echo [SUCCESS] Backend files found
echo.
echo Starting backend service...
echo API URL: http://127.0.0.1:8000
echo API Docs: http://127.0.0.1:8000/docs
echo Press Ctrl+C to stop service
echo.

python run.py

echo.
echo Backend service stopped
pause
