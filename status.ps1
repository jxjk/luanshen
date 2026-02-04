# Process Optimization System - Status Check Script
# PowerShell Version

# Change to script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Process Optimization System - Status Check" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker service
Write-Host "[1] Docker Service Status" -ForegroundColor Yellow
try {
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Docker Service: Running" -ForegroundColor Green
    } else {
        Write-Host "[X] Docker Service: Not running" -ForegroundColor Red
    }
} catch {
    Write-Host "[X] Docker Service: Not installed" -ForegroundColor Red
}

Write-Host ""

# Check container status
Write-Host "[2] Container Status" -ForegroundColor Yellow
$containers = docker-compose ps -q
if ($containers) {
    docker-compose ps
} else {
    Write-Host "[X] No running containers" -ForegroundColor Red
}

Write-Host ""

# Check port usage
Write-Host "[3] Port Usage" -ForegroundColor Yellow
$port3307 = Get-NetTCPConnection -LocalPort 3307 -ErrorAction SilentlyContinue
$port5007 = Get-NetTCPConnection -LocalPort 5007 -ErrorAction SilentlyContinue

if ($port3307) {
    Write-Host "[OK] Port 3307 (MySQL): In use" -ForegroundColor Green
} else {
    Write-Host "[O] Port 3307 (MySQL): Not in use" -ForegroundColor Gray
}

if ($port5007) {
    Write-Host "[OK] Port 5007 (API): In use" -ForegroundColor Green
} else {
    Write-Host "[O] Port 5007 (API): Not in use" -ForegroundColor Gray
}

Write-Host ""

# Check volumes
Write-Host "[4] Volume Status" -ForegroundColor Yellow
$volumes = docker volume ls --filter "name=mysql_data" --format "{{.Name}}"
if ($volumes) {
    Write-Host "[OK] Volumes:" -ForegroundColor Green
    foreach ($volume in $volumes) {
        Write-Host "  - $volume" -ForegroundColor White
    }
} else {
    Write-Host "[O] No volumes" -ForegroundColor Gray
}

Write-Host ""

# Health check
Write-Host "[5] Service Health Check" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5007/api/v1/optimization/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "[OK] Backend Service: Healthy" -ForegroundColor Green
    } else {
        Write-Host "[!] Backend Service: Abnormal (Status: $($response.StatusCode))" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[X] Backend Service: Cannot connect" -ForegroundColor Red
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Status Check Completed" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Quick Actions:" -ForegroundColor Green
Write-Host "  - View real-time logs: .\logs.ps1 -Follow" -ForegroundColor White
Write-Host "  - Restart services:    docker-compose restart" -ForegroundColor White
Write-Host "  - Stop services:       .\stop.ps1" -ForegroundColor White
Write-Host ""