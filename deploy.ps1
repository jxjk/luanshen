# Process Optimization System - Deployment Script
# PowerShell Version

# Change to script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath
Write-Host "Working directory: $PWD" -ForegroundColor Gray

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Process Optimization System - Deployment" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
Write-Host "[1/7] Checking Docker environment..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Docker installed: $dockerVersion" -ForegroundColor Green
    } else {
        Write-Host "[X] Docker not installed, please install Docker Desktop" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[X] Docker not installed, please install Docker Desktop" -ForegroundColor Red
    exit 1
}

# Check if Docker is running
Write-Host "[2/7] Checking Docker service status..." -ForegroundColor Yellow
try {
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Docker service is running" -ForegroundColor Green
    } else {
        Write-Host "[X] Docker service not running, please start Docker Desktop" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[X] Docker service not running, please start Docker Desktop" -ForegroundColor Red
    exit 1
}

# Check if Docker Compose is available
Write-Host "[3/7] Checking Docker Compose..." -ForegroundColor Yellow
try {
    $composeVersion = docker-compose --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Docker Compose installed: $composeVersion" -ForegroundColor Green
    } else {
        Write-Host "[X] Docker Compose not installed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[X] Docker Compose not installed" -ForegroundColor Red
    exit 1
}

# Check port usage
Write-Host "[4/7] Checking port usage..." -ForegroundColor Yellow
$port3307 = Get-NetTCPConnection -LocalPort 3307 -ErrorAction SilentlyContinue
$port5007 = Get-NetTCPConnection -LocalPort 5007 -ErrorAction SilentlyContinue

if ($port3307) {
    Write-Host "[!] Warning: Port 3307 already in use (MySQL)" -ForegroundColor Yellow
}
if ($port5007) {
    Write-Host "[!] Warning: Port 5007 already in use (Backend service)" -ForegroundColor Yellow
}
if (-not $port3307 -and -not $port5007) {
    Write-Host "[OK] All ports available" -ForegroundColor Green
}

# Create environment variable file if not exists
Write-Host "[5/7] Checking environment configuration..." -ForegroundColor Yellow
$envFile = ".env"
if (-not (Test-Path $envFile)) {
    Write-Host "[!] Creating .env file..." -ForegroundColor Yellow
    @"
DB_HOST=localhost
DB_PORT=3307
DB_USER=root
DB_PASSWORD=123456
DB_NAME=ga_tools
DB_CHARSET=utf8mb4

ALGO_POPULATION_SIZE=1024
ALGO_GENERATIONS=50
ALGO_CROSSOVER_RATE=0.6
ALGO_MUTATION_RATE=0.3

API_HOST=0.0.0.0
API_PORT=5007
API_RELOAD=true
API_WORKERS=1

SECRET_KEY=your-secret-key-change-in-production-123456
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

LOG_LEVEL=INFO
LOG_FILE=logs/app.log

ENVIRONMENT=development
"@ | Out-File -FilePath $envFile -Encoding UTF8
    Write-Host "[OK] .env file created" -ForegroundColor Green
} else {
    Write-Host "[OK] .env file already exists" -ForegroundColor Green
}

# Starting services
Write-Host "[6/7] Starting Docker Compose services..." -ForegroundColor Yellow
Write-Host "This may take a few minutes, please wait..." -ForegroundColor Gray

# Stopping and removing existing containers
Write-Host "Stopping existing containers..." -ForegroundColor Gray

# Stop and remove all containers for this project
$existingContainers = docker ps -a --filter "name=process_digital_twin" --format "{{.Names}}" 2>$null
if ($existingContainers) {
    Write-Host "Found existing containers: $existingContainers" -ForegroundColor Yellow
    docker-compose down -v 2>$null
    if ($LASTEXITCODE -ne 0) {
        # If docker-compose down fails, try manual removal
        foreach ($container in $existingContainers) {
            Write-Host "Removing container: $container" -ForegroundColor Gray
            docker stop $container 2>$null
            docker rm $container 2>$null
        }
    }
    Write-Host "[OK] Existing containers removed" -ForegroundColor Green
} else {
    Write-Host "[OK] No existing containers found" -ForegroundColor Green
}

# Clean up failed builds
Write-Host "Cleaning up previous builds..." -ForegroundColor Gray
docker builder prune -f 2>$null
Write-Host "[OK] Build cache cleaned" -ForegroundColor Green

# Build and start services
Write-Host "Building and starting services..." -ForegroundColor Gray
$composeResult = docker-compose up -d --build 2>&1
$exitCode = $LASTEXITCODE

if ($exitCode -eq 0) {
    Write-Host "[OK] Docker Compose services started successfully" -ForegroundColor Green
} else {
    Write-Host "[X] Docker Compose services failed to start" -ForegroundColor Red
    Write-Host "Error output:" -ForegroundColor Red
    Write-Host $composeResult -ForegroundColor Red
    Write-Host ""
    Write-Host "Tip: Try running 'docker builder prune -f' and 'docker-compose down' before deploying again" -ForegroundColor Yellow
    exit 1
}

# Wait for services to be ready
Write-Host "[7/7] Waiting for services to be ready..." -ForegroundColor Yellow
Write-Host "Checking MySQL database..." -ForegroundColor Gray
$mysqlReady = $false
$maxAttempts = 30
$attempt = 0

while (-not $mysqlReady -and $attempt -lt $maxAttempts) {
    $attempt++
    Start-Sleep -Seconds 2
    try {
        $result = docker exec process_digital_twin_mysql mysqladmin ping -h localhost -u root -p123456 2>&1
        if ($LASTEXITCODE -eq 0) {
            $mysqlReady = $true
            Write-Host "[OK] MySQL database is ready" -ForegroundColor Green
        }
    } catch {
        Write-Host "  Waiting for MySQL to start... ($attempt/$maxAttempts)" -ForegroundColor Gray
    }
}

if (-not $mysqlReady) {
    Write-Host "[!] MySQL startup timeout, please check logs" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Deployment Completed!" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Service Status:" -ForegroundColor Green
Write-Host "  - MySQL Database:     http://localhost:3307" -ForegroundColor White
Write-Host "  - Backend API:        http://localhost:5007" -ForegroundColor White
Write-Host "  - API Documentation:  http://localhost:5007/docs" -ForegroundColor White
Write-Host "  - Health Check:       http://localhost:5007/api/v1/optimization/health" -ForegroundColor White
Write-Host ""
Write-Host "Common Commands:" -ForegroundColor Green
Write-Host "  - View logs:          .\logs.ps1" -ForegroundColor White
Write-Host "  - Stop services:      .\stop.ps1" -ForegroundColor White
Write-Host "  - Restart services:   docker-compose restart" -ForegroundColor White
Write-Host "  - Clean data:         .\cleanup.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Green
Write-Host "  1. Visit http://localhost:5007/docs to view API documentation" -ForegroundColor White
Write-Host "  2. Add test data (materials, tools, machines, strategies)" -ForegroundColor White
Write-Host "  3. Start frontend: cd frontend && npm install && npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan