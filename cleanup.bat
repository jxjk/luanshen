@echo off
chcp 65001 >nul
echo ================================================================
echo   Cleanup All Data
echo ================================================================
echo.
echo Changing to script directory...
cd /d "%~dp0"
echo.
echo WARNING: This will delete all data!
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0cleanup.ps1"

pause