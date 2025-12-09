# ====================================
# Gerenciador do Serviço PSCInventario
# Comandos rápidos para gerenciar o serviço
# ====================================

param(
    [Parameter(Position=0)]
    [ValidateSet("start", "stop", "restart", "status", "logs")]
    [string]$Action = "status"
)

$ServiceName = "PSCInventarioBackend"
$ProjectRoot = "C:\Program Files (x86)\PSCInventario"
$NssmPath = "$ProjectRoot\service\nssm.exe"
$LogPath = "$ProjectRoot\service\logs"

switch ($Action) {
    "start" {
        Write-Host "Iniciando $ServiceName..." -ForegroundColor Yellow
        & $NssmPath start $ServiceName
        Start-Sleep -Seconds 2
        $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        if ($service.Status -eq "Running") {
            Write-Host "Servico iniciado com sucesso!" -ForegroundColor Green
        } else {
            Write-Host "Falha ao iniciar. Verifique os logs." -ForegroundColor Red
        }
    }
    "stop" {
        Write-Host "Parando $ServiceName..." -ForegroundColor Yellow
        & $NssmPath stop $ServiceName
        Write-Host "Servico parado." -ForegroundColor Green
    }
    "restart" {
        Write-Host "Reiniciando $ServiceName..." -ForegroundColor Yellow
        & $NssmPath restart $ServiceName
        Start-Sleep -Seconds 2
        $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        if ($service.Status -eq "Running") {
            Write-Host "Servico reiniciado com sucesso!" -ForegroundColor Green
        } else {
            Write-Host "Falha ao reiniciar. Verifique os logs." -ForegroundColor Red
        }
    }
    "status" {
        $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        if ($service) {
            Write-Host ""
            Write-Host "=== Status do Servico ===" -ForegroundColor Cyan
            Write-Host "Nome: $ServiceName" -ForegroundColor White
            Write-Host "Status: $($service.Status)" -ForegroundColor $(if ($service.Status -eq "Running") { "Green" } else { "Red" })
            Write-Host ""
            
            if ($service.Status -eq "Running") {
                Write-Host "URLs:" -ForegroundColor Yellow
                Write-Host "  API: http://10.200.10.57:8000" -ForegroundColor White
                Write-Host "  Docs: http://10.200.10.57:8000/docs" -ForegroundColor White
            }
        } else {
            Write-Host "Servico nao instalado." -ForegroundColor Red
            Write-Host "Execute: .\install_service.ps1" -ForegroundColor Yellow
        }
    }
    "logs" {
        Write-Host "=== Ultimas linhas do log ===" -ForegroundColor Cyan
        if (Test-Path "$LogPath\backend_stderr.log") {
            Write-Host ""
            Write-Host "--- Erros (stderr) ---" -ForegroundColor Red
            Get-Content "$LogPath\backend_stderr.log" -Tail 20
        }
        if (Test-Path "$LogPath\backend_stdout.log") {
            Write-Host ""
            Write-Host "--- Saida (stdout) ---" -ForegroundColor Green
            Get-Content "$LogPath\backend_stdout.log" -Tail 30
        }
    }
}
