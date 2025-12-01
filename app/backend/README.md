# Sistema de Inventário - Backend

Sistema web completo de inventário desenvolvido com FastAPI, MariaDB e autenticação JWT.

## 🚀 Tecnologias

- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para banco de dados
- **MariaDB/MySQL** - Banco de dados relacional
- **JWT** - Autenticação via tokens
- **Bcrypt** - Hash de senhas
- **Pydantic** - Validação de dados

## 📦 Instalação

### 1. Criar ambiente virtual

```bash
python -m venv venv
```

### 2. Ativar ambiente virtual

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Copie o arquivo `.env.example` para `.env` e ajuste as configurações:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações do banco de dados.

### 5. Configurar MariaDB

Crie o banco de dados:

```sql
CREATE DATABASE inventario CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6. Criar usuário admin (opcional)

Execute o script Python para criar um usuário administrador:

```python
from core.database import SessionLocal
from core.security import hash_password
from models.user import User, PlantaEnum, RoleEnum

db = SessionLocal()

admin = User(
    user_name="admin",
    senha_hash=hash_password("admin123"),
    planta=PlantaEnum.PS01,
    role=RoleEnum.ADMIN
)

db.add(admin)
db.commit()
db.close()

print("Usuário admin criado com sucesso!")
```

## 🏃 Executar

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

A API estará disponível em: `http://localhost:8000`

Documentação interativa (Swagger): `http://localhost:8000/docs`

## 📚 Estrutura do Projeto

```
backend/
├── main.py                 # Aplicação principal
├── api/
│   ├── auth.py            # Rotas de autenticação
│   ├── contagem.py        # Rotas de contagem
│   ├── exportacao.py      # Rotas de exportação
│   └── itens.py           # Rotas de itens
├── core/
│   ├── config.py          # Configurações
│   ├── database.py        # Conexão com banco
│   └── security.py        # Segurança e JWT
├── models/
│   ├── user.py            # Model de usuário
│   ├── itens.py           # Model de itens
│   └── forms_contagem.py  # Model de contagem
├── schemas/
│   ├── user.py            # Schemas de usuário
│   ├── itens.py           # Schemas de itens
│   └── contagem.py        # Schemas de contagem
└── utils/
    ├── jwt.py             # Utilitários JWT
    └── excel_export.py    # Exportação Excel/CSV
```

## 🔐 Autenticação

O sistema usa JWT (JSON Web Tokens) para autenticação. Faça login via `/auth/login` e use o token retornado no header `Authorization: Bearer <token>`.

## 👥 Papéis de Usuário

- **admin**: Acesso total
- **encarregado**: Contagem + Exportação
- **contador**: Apenas contagem

## 📊 Endpoints Principais

### Autenticação
- `POST /auth/login` - Login
- `GET /auth/me` - Dados do usuário autenticado

### Itens
- `GET /itens/` - Listar itens
- `GET /itens/part-numbers` - Listar part numbers

### Contagem
- `GET /contagem/sugerir` - Sugerir número de contagem
- `POST /contagem/salvar` - Salvar contagem

### Exportação
- `GET /exportacao/csv` - Exportar CSV
- `GET /exportacao/excel` - Exportar Excel

## 🛠️ Desenvolvimento

Para acessar a documentação automática da API:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📝 Licença

MIT
