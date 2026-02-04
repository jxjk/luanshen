# Process Optimization System - View Logs Script
# PowerShell Version

# Change to script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

param(
    [string]$Service = "",
    [switch]$Follow
)

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  View Service Logs" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

if ($Service) {
    Write-Host "Viewing service: $Service" -ForegroundColor Yellow
    if ($Follow) {
        docker-compose logs -f $Service
    } else {
        docker-compose logs $Service
    }
} else {
    Write-Host "Viewing all service logs" -ForegroundColor Yellow
    if ($Follow) {
        docker-compose logs -f
    } else {
        docker-compose logs
    }
}