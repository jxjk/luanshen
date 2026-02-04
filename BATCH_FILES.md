# Batch Files Guide

This guide explains how to use the batch files for deploying and managing the Process Optimization System.

## Available Batch Files

| File | Function | Description |
|------|----------|-------------|
| `deploy.bat` | Deployment | Deploy all services (MySQL + Backend) |
| `stop.bat` | Stop Services | Stop all running services |
| `status.bat` | Check Status | Check service status |
| `init.bat` | Initialize Data | Add test data to database |
| `logs.bat` | View Logs | View service logs |
| `cleanup.bat` | Cleanup Data | Clean up all data and services |

## Quick Start

### Step 1: Deploy Services

Double-click `deploy.bat` or run in Command Prompt:

```cmd
deploy.bat
```

### Step 2: Initialize Test Data

Double-click `init.bat` or run:

```cmd
init.bat
```

### Step 3: Start Frontend

Open a new Command Prompt and run:

```cmd
cd frontend
npm install
npm run dev
```

### Step 4: Access Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:5007
- API Docs: http://localhost:5007/docs

## Usage Examples

### Check Service Status

```cmd
status.bat
```

### View Logs

```cmd
logs.bat
```

### Stop Services

```cmd
stop.bat
```

### Restart Services

```cmd
stop.bat
deploy.bat
```

### Clean Up All Data

```cmd
cleanup.bat
deploy.bat
init.bat
```

## Troubleshooting

### Issue: Script fails with encoding errors

**Solution**: The batch files now use UTF-8 encoding (chcp 65001). If you still see encoding errors, try:

1. Open Command Prompt with administrator privileges
2. Run the batch file directly

### Issue: Docker not found

**Solution**: Ensure Docker Desktop is installed and running:
1. Download Docker Desktop from https://www.docker.com/products/docker-desktop
2. Install and start Docker Desktop
3. Run `deploy.bat` again

### Issue: Port already in use

**Solution**: Check if ports 3307 or 5007 are in use:

```cmd
netstat -ano | findstr :3307
netstat -ano | findstr :5007
```

If ports are occupied, either:
1. Stop the conflicting service, or
2. Modify the port mappings in `docker-compose.yml`

### Issue: Services not starting

**Solution**: Check logs:

```cmd
logs.bat
```

Or check detailed status:

```cmd
status.bat
```

## PowerShell Scripts

The batch files call the following PowerShell scripts:

- `deploy.ps1` - Main deployment script
- `stop.ps1` - Stop services script
- `status.ps1` - Status check script
- `logs.ps1` - Log viewing script
- `cleanup.ps1` - Cleanup script
- `init-data.ps1` - Data initialization script

You can also run these PowerShell scripts directly:

```powershell
powershell -ExecutionPolicy Bypass -File deploy.ps1
```

## Advanced Usage

### Customize Environment Variables

Edit the `.env` file in the project root:

```bash
DB_HOST=localhost
DB_PORT=3307
DB_USER=root
DB_PASSWORD=123456
DB_NAME=ga_tools

ALGO_POPULATION_SIZE=1024
ALGO_GENERATIONS=50
ALGO_CROSSOVER_RATE=0.6
ALGO_MUTATION_RATE=0.3

API_HOST=0.0.0.0
API_PORT=5007

SECRET_KEY=your-secret-key-change-in-production
```

After changing environment variables, restart services:

```cmd
stop.bat
deploy.bat
```

### View Specific Service Logs

Run the PowerShell script with parameters:

```powershell
powershell -ExecutionPolicy Bypass -File logs.ps1 -Service mysql
powershell -ExecutionPolicy Bypass -File logs.ps1 -Service parameter-optimization -Follow
```

## Important Notes

1. **Administrator Privileges**: All batch files require administrator privileges
2. **Docker Desktop**: Ensure Docker Desktop is running before deployment
3. **Default Ports**: MySQL (3307), API (5007)
4. **Data Persistence**: Data is stored in Docker volumes and persists between restarts
5. **Cleanup Warning**: `cleanup.bat` will delete all data - use with caution

## Support

For more information, see:
- [Deployment Guide](DEPLOYMENT.md)
- [Quick Start Guide](QUICKSTART.md)
- [Project Documentation](AGENTS.md)
- [API Documentation](http://localhost:5007/docs)