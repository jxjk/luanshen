@echo off
chcp 65001 >nul
echo ================================================================
echo   Service Status
echo ================================================================
echo.
echo Changing to script directory...
cd /d "%~dp0"
echo.
echo Checking service status...
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0status.ps1"

pause