# Configuração de Variáveis de Ambiente

## Backend (.env)

Crie um arquivo `.env` na pasta `app/backend/` com o seguinte conteúdo:

```env
# ====================================
# BANCO DE DADOS
# ====================================
# Formato: mysql+pymysql://USUARIO:SENHA@HOST:PORTA/BANCO
DATABASE_URL=mysql+pymysql://root:sua_senha@localhost:3306/inventario

# ====================================
# SEGURANÇA JWT
# ====================================
# IMPORTANTE: Mude SECRET_KEY em produção!
SECRET_KEY=sua-chave-secreta-super-segura-mude-isso-em-producao
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# ====================================
# CORS (URLs permitidas)
# ====================================
# Separe múltiplas URLs com vírgula
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# ====================================
# APLICAÇÃO
# ====================================
PROJECT_NAME=Sistema de Inventário
VERSION=1.0.0
```

## Descrição das Variáveis

### DATABASE_URL
**Obrigatório**: Sim  
**Descrição**: String de conexão com o banco de dados MariaDB/MySQL

**Formato**:
```
mysql+pymysql://[usuario]:[senha]@[host]:[porta]/[banco]
```

**Exemplos**:
```env
# Local (padrão)
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/inventario

# Servidor remoto
DATABASE_URL=mysql+pymysql://admin:senha123@192.168.1.100:3306/inventario

# Com caracteres especiais na senha (use URL encoding)
DATABASE_URL=mysql+pymysql://user:p%40ssw0rd@localhost:3306/inventario
```

### SECRET_KEY
**Obrigatório**: Sim  
**Descrição**: Chave secreta para assinar tokens JWT

**⚠️ IMPORTANTE**: 
- Use uma chave forte e aleatória em produção
- NUNCA compartilhe esta chave
- Mude-a se houver suspeita de comprometimento

**Como gerar uma chave segura**:
```python
import secrets
print(secrets.token_urlsafe(32))
```

### ALGORITHM
**Obrigatório**: Sim  
**Descrição**: Algoritmo de criptografia JWT  
**Valor padrão**: HS256  
**Outros valores possíveis**: HS384, HS512

### ACCESS_TOKEN_EXPIRE_MINUTES
**Obrigatório**: Não  
**Descrição**: Tempo de expiração do token em minutos  
**Valor padrão**: 1440 (24 horas)  

**Exemplos**:
- 60 = 1 hora
- 480 = 8 horas
- 1440 = 24 horas
- 10080 = 7 dias

### BACKEND_CORS_ORIGINS
**Obrigatório**: Não  
**Descrição**: URLs permitidas para fazer requisições CORS  
**Valor padrão**: http://localhost:3000,http://localhost:5173

**Exemplos**:
```env
# Desenvolvimento
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Produção
BACKEND_CORS_ORIGINS=https://meusite.com,https://www.meusite.com

# Múltiplos ambientes
BACKEND_CORS_ORIGINS=http://localhost:3000,https://dev.meusite.com,https://meusite.com
```

### PROJECT_NAME
**Obrigatório**: Não  
**Descrição**: Nome do projeto exibido na documentação  
**Valor padrão**: Sistema de Inventário

### VERSION
**Obrigatório**: Não  
**Descrição**: Versão da API  
**Valor padrão**: 1.0.0

## Frontend

O frontend não requer variáveis de ambiente por padrão. A URL da API está hardcoded em `src/services/api.js`.

Se desejar usar variáveis de ambiente no frontend, crie um arquivo `.env` na pasta `app/frontend/`:

```env
VITE_API_URL=http://localhost:8000
```

E atualize `src/services/api.js`:

```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

## Configuração para Diferentes Ambientes

### Desenvolvimento
```env
DATABASE_URL=mysql+pymysql://root:root@localhost:3306/inventario
SECRET_KEY=dev-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440
BACKEND_CORS_ORIGINS=http://localhost:3000
```

### Produção
```env
DATABASE_URL=mysql+pymysql://prod_user:strong_password@db.example.com:3306/inventario
SECRET_KEY=sua-chave-super-secreta-gerada-aleatoriamente
ACCESS_TOKEN_EXPIRE_MINUTES=480
BACKEND_CORS_ORIGINS=https://inventario.example.com
```

## Segurança

✅ **BOM**:
- Usar SECRET_KEY forte e aleatória
- Manter .env fora do controle de versão (Git)
- Usar senhas fortes no DATABASE_URL
- Limitar CORS apenas às origens necessárias

❌ **RUIM**:
- Commitar arquivo .env no Git
- Usar chaves simples como "123456"
- Permitir CORS para qualquer origem (*)
- Usar mesma SECRET_KEY em dev e prod

## Troubleshooting

### Erro: "No module named 'dotenv'"
```bash
pip install python-dotenv
```

### Erro: "Access denied for user"
Verifique usuário e senha no DATABASE_URL

### Erro: "Unknown database 'inventario'"
Crie o banco de dados:
```sql
CREATE DATABASE inventario;
```

### Token expira muito rápido
Aumente ACCESS_TOKEN_EXPIRE_MINUTES no .env

### CORS error no frontend
Adicione a URL do frontend em BACKEND_CORS_ORIGINS
