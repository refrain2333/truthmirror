@echo off
chcp 65001 >nul
title Truth Mirror - Frontend Server
color 0A
echo ====================================
echo    Truth Mirror - Frontend Server
echo ====================================
echo.

cd /d "%~dp0frontend"

echo Checking frontend directory...
if not exist "index.html" (
    echo [ERROR] index.html not found
    echo Please ensure you are running this script in the correct directory
    pause
    exit /b 1
)

echo [SUCCESS] Frontend files found
echo.
echo Starting frontend service...
echo Service URL: http://127.0.0.1:8080
echo Press Ctrl+C to stop service
echo.

python -m http.server 8080 --bind 127.0.0.1 --directory .

echo.
echo Frontend service stopped
pause