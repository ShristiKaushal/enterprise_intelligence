# Enterprise Intelligence Platform — Quick Start
# Run this from the project root: .\start.ps1

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Enterprise Intelligence Platform" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$root = $PSScriptRoot
$backend = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"

# Check if .env exists
if (-not (Test-Path (Join-Path $root ".env"))) {
    Write-Host "Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item (Join-Path $root ".env.example") (Join-Path $root ".env")
}

Write-Host "Starting backend (uvicorn)..." -ForegroundColor Green
$backendProcess = Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "cd '$backend'; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -PassThru

Start-Sleep -Seconds 2

Write-Host "Starting frontend (vite)..." -ForegroundColor Green
$frontendProcess = Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "cd '$frontend'; npm run dev" -PassThru

Write-Host ""
Write-Host "Both services starting:" -ForegroundColor Cyan
Write-Host "  Backend API:  http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs:     http://localhost:8000/api/docs" -ForegroundColor White
Write-Host "  Frontend:     http://localhost:5173" -ForegroundColor White
Write-Host ""
Write-Host "Login: admin@eip.local / Admin@12345" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press CTRL+C to stop (this window can be closed - services run in their own windows)" -ForegroundColor Gray
