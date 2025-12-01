# 🛠️ Comandos Úteis - Sistema de Inventário

## 📦 Backend (Python/FastAPI)

### Ambiente Virtual

```powershell
# Criar ambiente virtual
python -m venv venv

# Ativar (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Ativar (Windows CMD)
.\venv\Scripts\activate.bat

# Desativar
deactivate
```

### Dependências

```powershell
# Instalar dependências
pip install -r requirements.txt

# Atualizar dependências
pip install --upgrade -r requirements.txt

# Adicionar nova dependência
pip install nome-do-pacote
pip freeze > requirements.txt

# Listar dependências instaladas
pip list
```

### Servidor

```powershell
# Modo desenvolvimento (auto-reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Modo produção
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Com log específico
uvicorn main:app --reload --log-level debug

# Porta alternativa
uvicorn main:app --reload --port 8001
```

### Banco de Dados

```powershell
# Criar usuário admin
python create_admin.py

# Console Python interativo
python

# Dentro do console Python:
from core.database import SessionLocal, init_db
from models.user import User
from core.security import hash_password

# Criar tabelas
init_db()

# Criar usuário
db = SessionLocal()
user = User(
    user_name="novo_usuario",
    senha_hash=hash_password("senha123"),
    planta="PS01",
    role="contador"
)
db.add(user)
db.commit()
db.close()
```

### Testes (se implementar)

```powershell
# Instalar pytest
pip install pytest pytest-asyncio httpx

# Rodar testes
pytest

# Com coverage
pytest --cov=. --cov-report=html
```

## 🎨 Frontend (React/Vite)

### Dependências

```powershell
# Instalar dependências
npm install
# ou
yarn install

# Adicionar nova dependência
npm install nome-do-pacote
# ou
yarn add nome-do-pacote

# Remover dependência
npm uninstall nome-do-pacote
# ou
yarn remove nome-do-pacote

# Atualizar dependências
npm update
# ou
yarn upgrade
```

### Servidor

```powershell
# Modo desenvolvimento
npm run dev
# ou
yarn dev

# Build para produção
npm run build
# ou
yarn build

# Preview da build
npm run preview
# ou
yarn preview

# Limpar cache
npm cache clean --force
```

### Debugging

```powershell
# Verificar versões
node --version
npm --version

# Limpar node_modules e reinstalar
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
```

## 🗄️ Banco de Dados (MariaDB/MySQL)

### Conexão

```powershell
# Conectar ao MySQL
mysql -u root -p

# Conectar a banco específico
mysql -u root -p inventario

# Executar script SQL
mysql -u root -p < database_setup.sql

# Executar script em banco específico
mysql -u root -p inventario < dados_exemplo.sql

# Exportar banco
mysqldump -u root -p inventario > backup.sql

# Importar banco
mysql -u root -p inventario < backup.sql
```

### Comandos SQL Úteis

```sql
-- Ver todos os bancos
SHOW DATABASES;

-- Usar banco
USE inventario;

-- Ver tabelas
SHOW TABLES;

-- Ver estrutura de tabela
DESCRIBE user_table;
DESCRIBE itens_inventario;
DESCRIBE forms_contagem;

-- Contar registros
SELECT COUNT(*) FROM user_table;
SELECT COUNT(*) FROM itens_inventario;
SELECT COUNT(*) FROM forms_contagem;

-- Ver últimas contagens
SELECT * FROM forms_contagem ORDER BY timestamp DESC LIMIT 10;

-- Ver usuários
SELECT id, user_name, planta, role FROM user_table;

-- Criar usuário MySQL
CREATE USER 'inventario_user'@'localhost' IDENTIFIED BY 'senha_forte';
GRANT ALL PRIVILEGES ON inventario.* TO 'inventario_user'@'localhost';
FLUSH PRIVILEGES;

-- Backup de tabela específica
SELECT * FROM forms_contagem INTO OUTFILE '/tmp/contagem_backup.csv'
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n';

-- Resetar auto_increment
ALTER TABLE forms_contagem AUTO_INCREMENT = 1;

-- Ver índices
SHOW INDEX FROM forms_contagem;

-- Otimizar tabelas
OPTIMIZE TABLE user_table;
OPTIMIZE TABLE itens_inventario;
OPTIMIZE TABLE forms_contagem;
```

## 🔍 Debugging e Logs

### Backend

```powershell
# Ver logs detalhados
uvicorn main:app --reload --log-level debug

# Python console interativo
python -i create_admin.py

# Ver variáveis de ambiente
Get-ChildItem Env:
```

### Frontend

```javascript
// No navegador (F12 Console)

// Ver token armazenado
localStorage.getItem('token')

// Ver dados do usuário
JSON.parse(localStorage.getItem('user'))

// Limpar localStorage
localStorage.clear()

// Testar API manualmente
fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ user_name: 'admin', senha: 'admin123' })
})
.then(r => r.json())
.then(console.log)
```

## 🧹 Limpeza e Manutenção

```powershell
# Backend - Remover arquivos cache Python
Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force

# Frontend - Limpar build e cache
Remove-Item -Recurse -Force dist
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install

# Git - Ver status
git status

# Git - Commitar mudanças
git add .
git commit -m "Descrição das mudanças"

# Git - Ver histórico
git log --oneline
```

## 📊 Monitoramento

### Backend

```powershell
# Ver processos Python
Get-Process | Where-Object { $_.ProcessName -like "*python*" }

# Matar processo específico
Stop-Process -Id PROCESS_ID

# Ver uso de porta
netstat -ano | findstr :8000
```

### Frontend

```powershell
# Ver processos Node
Get-Process | Where-Object { $_.ProcessName -like "*node*" }

# Ver uso de porta
netstat -ano | findstr :3000
```

## 🔐 Segurança

### Gerar SECRET_KEY forte

```python
# Python
import secrets
print(secrets.token_urlsafe(32))
```

```powershell
# PowerShell
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))
```

### Hash de senha manualmente

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash("minha_senha")
print(hashed)
```

## 📦 Deploy

### Backend - Produção

```powershell
# Instalar gunicorn
pip install gunicorn

# Rodar com gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Com systemd (Linux)
# Criar arquivo /etc/systemd/system/inventario.service
```

### Frontend - Produção

```powershell
# Build
npm run build

# Servir com servidor web (nginx, apache, etc)
# Os arquivos estarão em: dist/
```

## 🔄 Atualizações

```powershell
# Backend - Atualizar pacotes
pip list --outdated
pip install --upgrade nome-do-pacote

# Frontend - Atualizar pacotes
npm outdated
npm update

# Verificar vulnerabilidades
npm audit
npm audit fix
```

## 📝 Scripts Personalizados

### Backup automático (PowerShell)

```powershell
# backup.ps1
$date = Get-Date -Format "yyyyMMdd_HHmmss"
$backupPath = "backups"

# Criar pasta de backups
New-Item -ItemType Directory -Force -Path $backupPath

# Backup do banco
mysqldump -u root -p inventario > "$backupPath/inventario_$date.sql"

Write-Host "Backup criado: $backupPath/inventario_$date.sql"
```

### Script de reset (desenvolvimento)

```powershell
# reset_dev.ps1
Write-Host "⚠️  Resetando ambiente de desenvolvimento..." -ForegroundColor Yellow

# Backend
cd app\backend
Remove-Item -Recurse -Force __pycache__ -ErrorAction SilentlyContinue
python create_admin.py

# Frontend
cd ..\frontend
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
npm run build

Write-Host "✅ Ambiente resetado!" -ForegroundColor Green
```

## 🆘 Troubleshooting Rápido

```powershell
# Erro: Porta em uso
# Encontrar processo
netstat -ano | findstr :8000
# Matar processo (substitua PID)
Stop-Process -Id PID -Force

# Erro: Módulo não encontrado
pip install -r requirements.txt

# Erro: node_modules corrompido
Remove-Item -Recurse -Force node_modules
npm install

# Erro: Banco não conecta
# Verificar se MariaDB está rodando
Get-Service | Where-Object { $_.Name -like "*mysql*" }

# Erro: CORS
# Adicionar URL no .env -> BACKEND_CORS_ORIGINS
```

---

💡 **Dica**: Salve estes comandos em um arquivo `.ps1` para reutilização rápida!
