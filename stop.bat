@echo off
chcp 65001 >nul
echo ================================================================
echo   Stop Services
echo ================================================================
echo.
echo Changing to script directory...
cd /d "%~dp0"
echo.
echo Stopping all services...
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0stop.ps1"

pause