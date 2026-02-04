# Process Optimization System - Cleanup Data Script
# PowerShell Version
# Warning: This script will delete all data, use with caution!

# Change to script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Clean Up Process Optimization System Data" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[!] WARNING: This will delete all data!" -ForegroundColor Red
Write-Host ""

# Confirm operation
$confirmation = Read-Host "Are you sure you want to clean up all data? (Type YES to continue)"
if ($confirmation -ne "YES") {
    Write-Host "Operation cancelled" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "[1/3] Stopping services..." -ForegroundColor Yellow
docker-compose down
Write-Host "[OK] Services stopped" -ForegroundColor Green

Write-Host "[2/3] Removing data volumes..." -ForegroundColor Yellow
docker volume rm process-digital-twin_mysql_data
docker volume rm process-digital-twin_optimization_logs
Write-Host "[OK] Data volumes removed" -ForegroundColor Green

Write-Host "[3/3] Cleaning unused images..." -ForegroundColor Yellow
docker image prune -f
Write-Host "[OK] Unused images cleaned" -ForegroundColor Green

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Cleanup Completed!" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Use .\deploy.ps1 to redeploy services" -ForegroundColor Green
Write-Host ""