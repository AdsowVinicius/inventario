# ====================================
# Iniciar Sistema em PRODUÇÃO - Windows
# ====================================

Write-Host "🚀 Iniciando Sistema de Inventário (Produção)" -ForegroundColor Cyan
Write-Host ""

$backendPath = "$PSScriptRoot\app\backend"
$frontendPath = "$PSScriptRoot\app\frontend"

# Backend
Write-Host "📦 Iniciando Backend (FastAPI) na porta 8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; & '.\env\Scripts\python.exe' -m uvicorn main:app --host 0.0.0.0 --port 8000"

Start-Sleep -Seconds 3

# Frontend (servidor de produção)
Write-Host "🎨 Iniciando Frontend (Produção) na porta 8080..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; python serve.py"

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "✅ Sistema iniciado com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 URLs:" -ForegroundColor Cyan
Write-Host "   Frontend: http://10.200.10.57:8080" -ForegroundColor White
Write-Host "   Backend:  http://10.200.10.57:8000" -ForegroundColor White
Write-Host "   API Docs: http://10.200.10.57:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Para parar os servidores, feche as janelas do PowerShell" -ForegroundColor Yellow
