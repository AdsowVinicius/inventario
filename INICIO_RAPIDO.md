# 🚀 Guia de Início Rápido

Este guia irá ajudá-lo a colocar o sistema rodando em minutos!

## ⚡ Passo a Passo

### 1️⃣ Configurar Banco de Dados

Abra o MySQL/MariaDB e execute:

```bash
mysql -u root -p < database_setup.sql
```

Ou execute manualmente no cliente MySQL:

```sql
CREATE DATABASE inventario CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2️⃣ Backend (FastAPI)

```powershell
# Navegar para o backend
cd app\backend

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt

# Copiar configurações
cp .env.example .env

# IMPORTANTE: Edite o arquivo .env com suas credenciais do banco!
# Abra o arquivo .env e ajuste DATABASE_URL

# Criar tabelas e usuário admin
python create_admin.py
```

### 3️⃣ Frontend (React)

Abra um novo terminal PowerShell:

```powershell
# Navegar para o frontend
cd app\frontend

# Instalar dependências
npm install
```

### 4️⃣ Iniciar o Sistema

**Opção A: Script Automático (Recomendado)**

Na pasta raiz do projeto:

```powershell
.\start.ps1
```

Isso abrirá duas janelas do PowerShell (backend e frontend).

**Opção B: Manual**

Terminal 1 (Backend):
```powershell
cd app\backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 (Frontend):
```powershell
cd app\frontend
npm run dev
```

### 5️⃣ Acessar o Sistema

🌐 **Frontend**: http://localhost:3000

📡 **Backend API**: http://localhost:8000

📚 **Documentação**: http://localhost:8000/docs

### 6️⃣ Fazer Login

Use as credenciais padrão:

- **Usuário**: `admin`
- **Senha**: `admin123`

⚠️ **IMPORTANTE**: Altere a senha após o primeiro acesso!

## 📋 Checklist de Instalação

- [ ] MariaDB/MySQL instalado e rodando
- [ ] Python 3.8+ instalado
- [ ] Node.js 16+ instalado
- [ ] Banco de dados `inventario` criado
- [ ] Dependências do backend instaladas
- [ ] Arquivo `.env` configurado no backend
- [ ] Tabelas criadas (via `create_admin.py`)
- [ ] Dependências do frontend instaladas
- [ ] Backend rodando na porta 8000
- [ ] Frontend rodando na porta 3000

## ❓ Problemas Comuns

### Erro de conexão com banco

Verifique o arquivo `app/backend/.env`:
```
DATABASE_URL=mysql+pymysql://SEU_USUARIO:SUA_SENHA@localhost:3306/inventario
```

### Porta já em uso

Altere as portas nos comandos:
- Backend: `--port 8001`
- Frontend: edite `vite.config.js` e mude `port: 3001`

### Token inválido após login

Limpe o localStorage do navegador:
1. F12 (DevTools)
2. Application > Local Storage
3. Limpar dados

### Erro ao instalar dependências Python

```powershell
# Use uma versão específica do Python
py -3.10 -m venv venv
```

## 🎯 Próximos Passos

1. ✅ Faça login com usuário admin
2. ✅ Explore a tela de Contagem
3. ✅ Teste a exportação (CSV/Excel)
4. ✅ Crie novos usuários se necessário
5. ✅ Insira dados reais de itens no banco

## 📞 Precisa de Ajuda?

Consulte os READMEs detalhados:
- `app/backend/README.md` - Documentação do backend
- `app/frontend/README.md` - Documentação do frontend
- `README.md` - Documentação geral

---

**Bom inventário! 📦✨**
