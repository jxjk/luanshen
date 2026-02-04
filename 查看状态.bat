@echo off
chcp 65001 >nul
echo ================================================================
echo   Check Service Status
echo ================================================================
echo.
echo Checking service status...
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0status.ps1"

pause