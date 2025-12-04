# ====================================
# Scripts de Inicialização - Windows
# ====================================

Write-Host "🚀 Iniciando Sistema de Inventário" -ForegroundColor Cyan
Write-Host ""

# Backend
Write-Host "📦 Iniciando Backend (FastAPI)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\app\backend'; .\venv\Scripts\Activate.ps1; uvicorn main:app --reload --host 0.0.0.0 --port 8000"

Start-Sleep -Seconds 2

# Frontend
Write-Host "🎨 Iniciando Frontend (React)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\app\frontend'; npm run dev"

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "✅ Sistema iniciado com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 URLs:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   Backend:  http://10.200.10.57:8000" -ForegroundColor White
Write-Host "   API Docs: http://10.200.10.57:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Para parar os servidores, feche as janelas do PowerShell" -ForegroundColor Yellow
