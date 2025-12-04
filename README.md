# 📦 Sistema de Inventário

Sistema web completo de inventário desenvolvido com **FastAPI** (backend), **MariaDB** (banco de dados) e **React** (frontend).

## 🚀 Características

- ✅ Interface 100% em **PT-BR**
- ✅ Autenticação JWT com bcrypt
- ✅ Controle de acesso por papéis (admin, encarregado, contador)
- ✅ Sugestão automática do número de contagem
- ✅ Exportação para CSV e Excel
- ✅ Design responsivo e moderno
- ✅ API RESTful completa

## 📋 Requisitos

- Python 3.8+
- Node.js 16+
- MariaDB 10.5+

## 🗄️ Estrutura do Projeto

```
app/
├── backend/              # API FastAPI
│   ├── main.py          # Aplicação principal
│   ├── api/             # Rotas da API
│   ├── core/            # Configurações e segurança
│   ├── models/          # Models SQLAlchemy
│   ├── schemas/         # Schemas Pydantic
│   └── utils/           # Utilitários
│
└── frontend/            # Interface React
    ├── src/
    │   ├── pages/       # Páginas
    │   ├── components/  # Componentes
    │   └── services/    # Serviços API
    └── ...
```

## 🔧 Instalação

### 1. Clonar o repositório

```bash
cd c:\Users\ABatista1\Desktop\inventario
```

### 2. Configurar Banco de Dados

Execute o script SQL para criar o banco:

```sql
CREATE DATABASE inventario CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Backend - FastAPI

```bash
cd app/backend

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt

# Copiar e configurar .env
cp .env.example .env
# Edite o arquivo .env com suas configurações

# Criar tabelas e usuário admin
python create_admin.py
```

### 4. Frontend - React

```bash
cd app/frontend

# Instalar dependências
npm install

# ou com yarn
yarn install
```

## 🏃 Executar

### Backend

```bash
cd app/backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Acesse:
- API: http://10.200.10.57:8000
- Documentação: http://10.200.10.57:8000/docs

### Frontend

```bash
cd app/frontend
npm run dev
```

Acesse: http://localhost:3000

## 👥 Usuários e Papéis

### Papéis disponíveis:

- **admin**: Acesso total ao sistema
- **encarregado**: Contagem + Exportação
- **contador**: Apenas contagem

### Usuário padrão (após executar create_admin.py):

- **Usuário**: `admin`
- **Senha**: `admin123`
- ⚠️ **IMPORTANTE**: Altere a senha após o primeiro login!

## 🗄️ Estrutura do Banco

### Tabela: user_table
- id
- user_name
- senha_hash
- planta (PS01, PS02, PS03, PS05, PS09, PB82)
- role (admin, encarregado, contador)

### Tabela: itens_inventario
- id
- num_material
- txt_descrica_material
- planta
- deposito
- tipo_material
- und_medida

### Tabela: forms_contagem
- id
- planta
- num_contagem
- zona_inventario
- etiqueta_inventario
- part_number
- campo
- qtd
- usuario_id
- timestamp

## 📊 Funcionalidades

### 🔐 Login
- Autenticação com JWT
- Validação de credenciais
- Redirecionamento automático

### 📝 Contagem
- Sugestão automática do número de contagem
- Dropdown dinâmico de part numbers
- Validação de campos obrigatórios
- Feedback visual de sucesso/erro

### 📤 Exportação
- Filtros opcionais por planta, zona, etiqueta, part number e número de contagem
- Exportação para CSV
- Exportação para Excel com formatação
- Download automático

## 🔒 Segurança

- Senhas criptografadas com bcrypt
- Tokens JWT com expiração configurável
- Proteção de rotas por autenticação
- Controle de acesso por papel
- CORS configurado

## 📚 API Endpoints

### Autenticação
- `POST /auth/login` - Login
- `GET /auth/me` - Dados do usuário

### Itens
- `GET /itens/` - Listar itens
- `GET /itens/part-numbers` - Part numbers

### Contagem
- `GET /contagem/sugerir` - Sugerir número
- `POST /contagem/salvar` - Salvar contagem

### Exportação
- `GET /exportacao/csv` - Exportar CSV
- `GET /exportacao/excel` - Exportar Excel

## 🛠️ Tecnologias

### Backend
- FastAPI
- SQLAlchemy
- Pydantic
- JWT (python-jose)
- Bcrypt
- Uvicorn
- OpenPyXL

### Frontend
- React 18
- React Router DOM
- Axios
- Vite
- CSS3

## 📝 Desenvolvimento

### Acessar documentação da API
- Swagger UI: http://10.200.10.57:8000/docs
- ReDoc: http://10.200.10.57:8000/redoc

### Criar novos usuários

Use o endpoint da API ou crie manualmente no banco:

```python
from core.database import SessionLocal
from core.security import hash_password
from models.user import User, PlantaEnum, RoleEnum

db = SessionLocal()

novo_usuario = User(
    user_name="usuario_teste",
    senha_hash=hash_password("senha123"),
    planta=PlantaEnum.PS01,
    role=RoleEnum.CONTADOR
)

db.add(novo_usuario)
db.commit()
db.close()
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

MIT License - Sinta-se livre para usar este projeto!

## 📞 Suporte

Para problemas ou dúvidas, consulte a documentação ou abra uma issue.

---

Desenvolvido com ❤️ usando Python, React e MariaDB
