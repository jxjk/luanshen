@echo off
chcp 65001 >nul
echo ================================================================
echo   Initialize Test Data
echo ================================================================
echo.
echo Initializing test data...
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0init-data.ps1"

pause