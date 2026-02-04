@echo off
chcp 65001 >nul
echo ================================================================
echo   Process Optimization System - Deployment
echo ================================================================
echo.
echo Note: Run as Administrator
echo.
echo Changing to script directory...
cd /d "%~dp0"
echo Current directory: %CD%
echo.
echo Starting deployment...
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0deploy.ps1"

pause