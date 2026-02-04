# Process Optimization System - Stop Services Script
# PowerShell Version

# Change to script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Stop Process Optimization System" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Stopping Docker Compose services..." -ForegroundColor Yellow
docker-compose down

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Services stopped" -ForegroundColor Green
} else {
    Write-Host "[X] Failed to stop services" -ForegroundColor Red
}

Write-Host ""
Write-Host "Hint: Use .\deploy.ps1 to restart services" -ForegroundColor Gray
Write-Host ""