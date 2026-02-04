@echo off
chcp 65001 >nul
echo ================================================================
echo   Stop Process Optimization System
echo ================================================================
echo.
echo Stopping services...
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0stop.ps1"

pause