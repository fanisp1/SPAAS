# SPAAS Startup Script
# This script starts both the Python backend and Next.js frontend

Write-Host "🚀 Starting SPAAS Application..." -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".\myvenv\Scripts\Activate.ps1")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: python -m venv myvenv" -ForegroundColor Yellow
    exit 1
}

# Check if frontend node_modules exists
if (-not (Test-Path ".\frontend\node_modules")) {
    Write-Host "⚠️  Frontend dependencies not installed" -ForegroundColor Yellow
    Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
    Set-Location frontend
    npm install
    Set-Location ..
}

Write-Host "📦 Activating Python virtual environment..." -ForegroundColor Cyan
& .\myvenv\Scripts\Activate.ps1

Write-Host "🐍 Starting Python backend on port 8000..." -ForegroundColor Cyan
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; & '$PWD\myvenv\Scripts\Activate.ps1'; uvicorn app.main:app --reload" -WindowStyle Normal

Write-Host "⏳ Waiting for backend to start..." -ForegroundColor Cyan
Start-Sleep -Seconds 3

Write-Host "⚛️  Starting Next.js frontend on port 3000..." -ForegroundColor Cyan
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm run dev" -WindowStyle Normal

Write-Host ""
Write-Host "✅ SPAAS is starting up!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "📍 API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "📍 Frontend: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "⏳ Waiting for services to fully start..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "🌐 Opening browser..." -ForegroundColor Cyan
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "✨ SPAAS is ready!" -ForegroundColor Green
Write-Host "Press Ctrl+C in the backend or frontend windows to stop" -ForegroundColor Yellow
