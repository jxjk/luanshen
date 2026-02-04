@echo off
chcp 65001 >nul
echo ================================================================
echo   Process Optimization System - One-Click Deployment
echo ================================================================
echo.
echo Note: This script requires administrator privileges
echo.
echo Starting PowerShell deployment script...
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0deploy.ps1"

pause