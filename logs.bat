@echo off
chcp 65001 >nul
echo ================================================================
echo   View Service Logs
echo ================================================================
echo.
echo Changing to script directory...
cd /d "%~dp0"
echo.
echo Viewing service logs...
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0logs.ps1"

pause