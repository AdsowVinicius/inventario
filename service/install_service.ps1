# ====================================
# Instalador do Serviço Windows - PSCInventario Backend
# Requer execução como Administrador
# ====================================

param(
    [switch]$Uninstall
)

$ServiceName = "PSCInventarioBackend"
$ServiceDisplayName = "PSCInventario - Backend API"
$ServiceDescription = "Servidor FastAPI do Sistema de Inventário PSC"

$ProjectRoot = "C:\Program Files (x86)\PSCInventario"
$BackendPath = "$ProjectRoot\app\backend"
$PythonPath = "$BackendPath\env\Scripts\python.exe"
$NssmPath = "$ProjectRoot\service\nssm.exe"

# Verificar se está rodando como administrador
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "ERRO: Este script precisa ser executado como Administrador!" -ForegroundColor Red
    Write-Host "Clique com botao direito no PowerShell e selecione 'Executar como Administrador'" -ForegroundColor Yellow
    exit 1
}

# Verificar se NSSM existe
if (-not (Test-Path $NssmPath)) {
    Write-Host "ERRO: NSSM nao encontrado em: $NssmPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Baixe o NSSM de: https://nssm.cc/download" -ForegroundColor Yellow
    Write-Host "Extraia e copie 'nssm.exe' (versao win64) para: $ProjectRoot\service\" -ForegroundColor Yellow
    exit 1
}

# Desinstalar serviço
if ($Uninstall) {
    Write-Host "Parando servico $ServiceName..." -ForegroundColor Yellow
    & $NssmPath stop $ServiceName 2>$null
    
    Write-Host "Removendo servico $ServiceName..." -ForegroundColor Yellow
    & $NssmPath remove $ServiceName confirm
    
    Write-Host "Servico removido com sucesso!" -ForegroundColor Green
    exit 0
}

# Verificar se Python existe
if (-not (Test-Path $PythonPath)) {
    Write-Host "ERRO: Python nao encontrado em: $PythonPath" -ForegroundColor Red
    exit 1
}

# Parar serviço existente (se houver)
Write-Host "Verificando servico existente..." -ForegroundColor Yellow
$existingService = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($existingService) {
    Write-Host "Parando servico existente..." -ForegroundColor Yellow
    & $NssmPath stop $ServiceName 2>$null
    Start-Sleep -Seconds 2
    & $NssmPath remove $ServiceName confirm 2>$null
    Start-Sleep -Seconds 1
}

# Instalar serviço
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Instalando Servico: $ServiceDisplayName" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Criar o serviço
Write-Host "Criando servico..." -ForegroundColor Yellow
& $NssmPath install $ServiceName $PythonPath

# Configurar argumentos
Write-Host "Configurando argumentos..." -ForegroundColor Yellow
& $NssmPath set $ServiceName AppParameters "-m uvicorn main:app --host 0.0.0.0 --port 8000"

# Configurar diretório de trabalho
Write-Host "Configurando diretorio..." -ForegroundColor Yellow
& $NssmPath set $ServiceName AppDirectory $BackendPath

# Configurar nome de exibição e descrição
& $NssmPath set $ServiceName DisplayName $ServiceDisplayName
& $NssmPath set $ServiceName Description $ServiceDescription

# Configurar para iniciar automaticamente
& $NssmPath set $ServiceName Start SERVICE_AUTO_START

# Configurar reinício automático em caso de falha
& $NssmPath set $ServiceName AppExit Default Restart
& $NssmPath set $ServiceName AppRestartDelay 5000

# Configurar logs
$LogPath = "$ProjectRoot\service\logs"
if (-not (Test-Path $LogPath)) {
    New-Item -ItemType Directory -Path $LogPath -Force | Out-Null
}
& $NssmPath set $ServiceName AppStdout "$LogPath\backend_stdout.log"
& $NssmPath set $ServiceName AppStderr "$LogPath\backend_stderr.log"
& $NssmPath set $ServiceName AppRotateFiles 1
& $NssmPath set $ServiceName AppRotateBytes 1048576

# Iniciar o serviço
Write-Host ""
Write-Host "Iniciando servico..." -ForegroundColor Yellow
& $NssmPath start $ServiceName

Start-Sleep -Seconds 3

# Verificar status
$service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($service -and $service.Status -eq "Running") {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "SERVICO INSTALADO COM SUCESSO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Nome: $ServiceName" -ForegroundColor White
    Write-Host "Status: Rodando" -ForegroundColor Green
    Write-Host "URL: http://10.200.10.57:8000" -ForegroundColor Cyan
    Write-Host "Docs: http://10.200.10.57:8000/docs" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Comandos uteis:" -ForegroundColor Yellow
    Write-Host "  Parar:     nssm stop $ServiceName" -ForegroundColor White
    Write-Host "  Iniciar:   nssm start $ServiceName" -ForegroundColor White
    Write-Host "  Reiniciar: nssm restart $ServiceName" -ForegroundColor White
    Write-Host "  Status:    nssm status $ServiceName" -ForegroundColor White
    Write-Host "  Remover:   .\install_service.ps1 -Uninstall" -ForegroundColor White
    Write-Host ""
    Write-Host "Logs em: $LogPath" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "ERRO: Servico nao iniciou corretamente!" -ForegroundColor Red
    Write-Host "Verifique os logs em: $LogPath" -ForegroundColor Yellow
}
