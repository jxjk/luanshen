# Process Optimization System - Initialize Test Data Script
# PowerShell Version

# Change to script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Initialize Test Data" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if service is running
Write-Host "[1/5] Checking service status..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5007/api/v1/optimization/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "[OK] Backend service is running" -ForegroundColor Green
    } else {
        Write-Host "[X] Backend service error, please start service first" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[X] Backend service not running, please run .\deploy.ps1 first" -ForegroundColor Red
    exit 1
}

Write-Host "[2/5] Adding material data..." -ForegroundColor Yellow
$materialBody = @{
    caiLiaoZu = "P1"
    name = "45 Steel"
    rm_min = 600
    rm_max = 750
    kc11 = 1800
    mc = 0.15
} | ConvertTo-Json

try {
    Invoke-WebRequest -Uri "http://localhost:5007/api/v1/materials" -Method Post -Body $materialBody -ContentType "application/json" -UseBasicParsing | Out-Null
    Write-Host "[OK] Material data added" -ForegroundColor Green
} catch {
    Write-Host "[!] Material data may already exist" -ForegroundColor Yellow
}

Write-Host "[3/5] Adding tool data..." -ForegroundColor Yellow
$toolBody = @{
    name = "Carbide End Mill"
    type = "milling"
    zhiJing = 25
    chiShu = 2
    vc_max = 150
    fz_max = 0.3
    ct = 180
    s_xiShu = 0.2
    f_xiShu = 0.14
    ap_xiShu = 0.26
    ap_max = 5.0
    ff_max = 800
    daoJianR = 0.8
    zhuPianJiao = 31
    qianJiao = 0
} | ConvertTo-Json

try {
    Invoke-WebRequest -Uri "http://localhost:5007/api/v1/tools" -Method Post -Body $toolBody -ContentType "application/json" -UseBasicParsing | Out-Null
    Write-Host "[OK] Tool data added" -ForegroundColor Green
} catch {
    Write-Host "[!] Tool data may already exist" -ForegroundColor Yellow
}

Write-Host "[4/5] Adding machine data..." -ForegroundColor Yellow
$machineBody = @{
    name = "XK7132 Milling Machine"
    type = "milling"
    pw_max = 7.5
    rp_max = 3000
    tnm_max = 45
    xiaoLv = 0.85
    f_max = 6000
} | ConvertTo-Json

try {
    Invoke-WebRequest -Uri "http://localhost:5007/api/v1/machines" -Method Post -Body $machineBody -ContentType "application/json" -UseBasicParsing | Out-Null
    Write-Host "[OK] Machine data added" -ForegroundColor Green
} catch {
    Write-Host "[!] Machine data may already exist" -ForegroundColor Yellow
}

Write-Host "[5/5] Adding strategy data..." -ForegroundColor Yellow
$strategyBody = @{
    name = "Rough Milling Strategy"
    type = "milling"
    rx_min = 12.5
    rz_min = 50
    lft_min = 30
    ae = 8.5
    moSunXiShu = 1.0
} | ConvertTo-Json

try {
    Invoke-WebRequest -Uri "http://localhost:5007/api/v1/strategies" -Method Post -Body $strategyBody -ContentType "application/json" -UseBasicParsing | Out-Null
    Write-Host "[OK] Strategy data added" -ForegroundColor Green
} catch {
    Write-Host "[!] Strategy data may already exist" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Test Data Initialization Completed!" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test data added:" -ForegroundColor Green
Write-Host "  - Material: 45 Steel (P1)" -ForegroundColor White
Write-Host "  - Tool: Carbide End Mill (25mm, 2 teeth)" -ForegroundColor White
Write-Host "  - Machine: XK7132 Milling Machine" -ForegroundColor White
Write-Host "  - Strategy: Rough Milling Strategy" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Green
Write-Host "  1. Visit http://localhost:5007/docs to test API" -ForegroundColor White
Write-Host "  2. Start frontend: cd frontend && npm run dev" -ForegroundColor White
Write-Host "  3. Perform parameter optimization in frontend" -ForegroundColor White
Write-Host ""