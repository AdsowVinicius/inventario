# ====================================
# Serviço Windows - PSCInventario Backend
# ====================================

## Pré-requisitos

1. **NSSM (Non-Sucking Service Manager)**
   - Baixe de: https://nssm.cc/download
   - Extraia o arquivo ZIP
   - Copie `nssm.exe` (da pasta win64) para: `C:\Program Files (x86)\PSCInventario\service\`

## Instalação do Serviço

1. Abra o **PowerShell como Administrador**
2. Execute:
   ```powershell
   cd "C:\Program Files (x86)\PSCInventario\service"
   .\install_service.ps1
   ```

## Gerenciamento do Serviço

### Via PowerShell (na pasta service):
```powershell
.\manage_service.ps1 status    # Ver status
.\manage_service.ps1 start     # Iniciar
.\manage_service.ps1 stop      # Parar
.\manage_service.ps1 restart   # Reiniciar
.\manage_service.ps1 logs      # Ver logs
```

### Via Windows Services:
1. Pressione `Win + R`
2. Digite `services.msc`
3. Procure por "PSCInventario - Backend API"

### Via NSSM diretamente:
```powershell
nssm start PSCInventarioBackend
nssm stop PSCInventarioBackend
nssm restart PSCInventarioBackend
nssm status PSCInventarioBackend
nssm edit PSCInventarioBackend    # Interface gráfica
```

## Desinstalar o Serviço

```powershell
cd "C:\Program Files (x86)\PSCInventario\service"
.\install_service.ps1 -Uninstall
```

## Logs

Os logs ficam em:
- `C:\Program Files (x86)\PSCInventario\service\logs\backend_stdout.log`
- `C:\Program Files (x86)\PSCInventario\service\logs\backend_stderr.log`

## Configurações do Serviço

| Configuração | Valor |
|-------------|-------|
| Nome | PSCInventarioBackend |
| Inicialização | Automática |
| Reinício em falha | Sim (após 5 segundos) |
| Porta | 8000 |
| URL | http://10.200.10.57:8000 |

## Solução de Problemas

### Serviço não inicia
1. Verifique os logs em `service\logs\`
2. Confirme que o MySQL está rodando
3. Teste manualmente:
   ```powershell
   cd "C:\Program Files (x86)\PSCInventario\app\backend"
   .\env\Scripts\Activate.ps1
   python -m uvicorn main:app --host 0.0.0.0 --port 8000
   ```

### Porta 8000 em uso
1. Verifique qual processo está usando:
   ```powershell
   netstat -ano | findstr :8000
   ```
2. Mate o processo ou altere a porta no serviço
