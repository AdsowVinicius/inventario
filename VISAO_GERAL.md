# 📋 Visão Geral do Sistema de Inventário

## 🎯 Objetivo

Sistema web completo para gerenciamento de inventário com funcionalidades de contagem, controle de acesso e exportação de dados.

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                      │
│  ┌────────────┐  ┌────────────┐  ┌─────────────┐           │
│  │   Login    │  │  Contagem  │  │ Exportação  │           │
│  └────────────┘  └────────────┘  └─────────────┘           │
│                        ↓ HTTP/REST API                       │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                       │
│  ┌──────────┐  ┌───────────┐  ┌────────────┐               │
│  │   Auth   │  │  Contagem │  │ Exportação │               │
│  │   JWT    │  │  Lógica   │  │  CSV/Excel │               │
│  └──────────┘  └───────────┘  └────────────┘               │
│                        ↓ SQLAlchemy                          │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    DATABASE (MariaDB)                        │
│  ┌─────────────┐  ┌──────────────────┐  ┌──────────────┐   │
│  │ user_table  │  │ itens_inventario │  │forms_contagem│   │
│  └─────────────┘  └──────────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Estrutura de Arquivos

```
inventario/
│
├── 📄 README.md                    # Documentação principal
├── 📄 INICIO_RAPIDO.md            # Guia de início rápido
├── 📄 CONFIGURACAO_ENV.md         # Guia de variáveis de ambiente
├── 📄 database_setup.sql          # Script de criação do banco
├── 📄 dados_exemplo.sql           # Dados de exemplo
├── 🔧 start.ps1                   # Script de inicialização
├── 📄 .gitignore                  # Arquivos ignorados pelo Git
│
└── 📁 app/
    │
    ├── 📁 backend/                # API FastAPI
    │   ├── 📄 main.py            # Aplicação principal
    │   ├── 📄 create_admin.py    # Script criar admin
    │   ├── 📄 requirements.txt   # Dependências Python
    │   ├── 📄 .env.example       # Exemplo de configuração
    │   ├── 📄 README.md          # Doc do backend
    │   │
    │   ├── 📁 api/               # Rotas da API
    │   │   ├── auth.py           # Autenticação
    │   │   ├── contagem.py       # Contagem
    │   │   ├── exportacao.py     # Exportação
    │   │   └── itens.py          # Itens
    │   │
    │   ├── 📁 core/              # Núcleo do sistema
    │   │   ├── config.py         # Configurações
    │   │   ├── database.py       # Conexão DB
    │   │   └── security.py       # Segurança/JWT
    │   │
    │   ├── 📁 models/            # Models SQLAlchemy
    │   │   ├── user.py           # Model usuário
    │   │   ├── itens.py          # Model itens
    │   │   └── forms_contagem.py # Model contagem
    │   │
    │   ├── 📁 schemas/           # Schemas Pydantic
    │   │   ├── user.py           # Schema usuário
    │   │   ├── itens.py          # Schema itens
    │   │   └── contagem.py       # Schema contagem
    │   │
    │   └── 📁 utils/             # Utilitários
    │       ├── jwt.py            # Funções JWT
    │       └── excel_export.py   # Exportação
    │
    └── 📁 frontend/              # Interface React
        ├── 📄 index.html         # HTML base
        ├── 📄 package.json       # Dependências Node
        ├── 📄 vite.config.js     # Config Vite
        ├── 📄 .gitignore         # Git ignore
        ├── 📄 README.md          # Doc do frontend
        │
        └── 📁 src/
            ├── 📄 index.jsx      # Ponto de entrada
            ├── 📄 index.css      # Estilos globais
            │
            ├── 📁 pages/         # Páginas
            │   ├── Login.jsx     # Tela login
            │   ├── Login.css
            │   ├── Contagem.jsx  # Tela contagem
            │   ├── Contagem.css
            │   ├── Exportacao.jsx # Tela exportação
            │   └── Exportacao.css
            │
            ├── 📁 components/    # Componentes
            │   ├── Navbar.jsx    # Barra navegação
            │   ├── Navbar.css
            │   └── ProtectedRoute.jsx
            │
            └── 📁 services/      # Serviços
                └── api.js        # Cliente API
```

## 🔐 Fluxo de Autenticação

```
1. Usuário envia credenciais → POST /auth/login
2. Backend valida com bcrypt
3. Backend gera token JWT contendo:
   - id
   - user_name
   - planta
   - role
4. Frontend armazena token no localStorage
5. Requisições subsequentes incluem: Authorization: Bearer <token>
6. Backend valida token e autoriza acesso
```

## 📝 Fluxo de Contagem

```
1. Usuário acessa /contagem
2. Frontend carrega part numbers da planta
3. Usuário preenche formulário:
   - Planta (pré-selecionada)
   - Zona de Inventário
   - Etiqueta
   - Part Number (dropdown)
   - Campo (opcional)
   - Quantidade
4. Sistema sugere num_contagem automaticamente:
   → GET /contagem/sugerir?pn=X&etiqueta=Y&planta=Z
   → Retorna próximo número baseado em registros existentes
5. Usuário confirma ou ajusta número
6. Dados enviados → POST /contagem/salvar
7. Backend salva com usuario_id e timestamp
8. Feedback visual de sucesso
```

## 📤 Fluxo de Exportação

```
1. Usuário (admin/encarregado) acessa /exportacao
2. Aplica filtros opcionais:
   - Planta
   - Zona
   - Etiqueta
   - Part Number
   - Número da Contagem
3. Clica em "Exportar CSV" ou "Exportar Excel"
4. Backend filtra dados e gera arquivo
5. Arquivo é baixado automaticamente
```

## 🎨 Tecnologias e Justificativas

### Backend: FastAPI
- ✅ Performance superior (async/await)
- ✅ Validação automática com Pydantic
- ✅ Documentação interativa (Swagger)
- ✅ Type hints nativos
- ✅ Fácil manutenção

### Database: MariaDB
- ✅ Open source e gratuito
- ✅ Compatível com MySQL
- ✅ Performance robusta
- ✅ Suporte a transações
- ✅ Amplamente usado

### Frontend: React
- ✅ Componentização
- ✅ Virtual DOM (performance)
- ✅ Ecossistema rico
- ✅ Fácil manutenção
- ✅ Hooks modernos

### Build Tool: Vite
- ✅ Extremamente rápido
- ✅ Hot Module Replacement
- ✅ Build otimizado
- ✅ Simples de configurar

### Auth: JWT + Bcrypt
- ✅ Stateless (escalável)
- ✅ Bcrypt protege senhas
- ✅ Token contém dados do usuário
- ✅ Expiração configurável

## 📈 Escalabilidade

### Melhorias Futuras Possíveis:

1. **Backend**
   - Adicionar Redis para cache
   - Implementar rate limiting
   - Adicionar logs estruturados
   - Implementar testes unitários
   - Adicionar migrations com Alembic

2. **Frontend**
   - Adicionar estado global (Redux/Zustand)
   - Implementar PWA
   - Adicionar testes (Jest/Testing Library)
   - Lazy loading de rotas
   - Otimização de bundle

3. **Database**
   - Índices adicionais
   - Particionamento de tabelas
   - Backup automático
   - Read replicas

4. **DevOps**
   - Docker containers
   - CI/CD pipeline
   - Monitoramento (Prometheus/Grafana)
   - Load balancer

## 🔒 Segurança Implementada

- ✅ Senhas hasheadas com bcrypt
- ✅ Tokens JWT com expiração
- ✅ Validação de entrada (Pydantic)
- ✅ CORS configurado
- ✅ Controle de acesso por papel
- ✅ SQL Injection protegido (SQLAlchemy)
- ✅ XSS protegido (React escapa automaticamente)

## 📊 Papéis e Permissões

| Papel       | Login | Contagem | Exportação | Gerenciar Usuários |
|-------------|-------|----------|------------|--------------------|
| contador    | ✅    | ✅       | ❌         | ❌                 |
| encarregado | ✅    | ✅       | ✅         | ❌                 |
| admin       | ✅    | ✅       | ✅         | ✅*                |

*Gerenciar usuários pode ser implementado futuramente

## 📞 Suporte

Para dúvidas, consulte:
1. `INICIO_RAPIDO.md` - Setup inicial
2. `README.md` - Documentação completa
3. `CONFIGURACAO_ENV.md` - Variáveis de ambiente
4. `app/backend/README.md` - Detalhes do backend
5. `app/frontend/README.md` - Detalhes do frontend

---

**Sistema desenvolvido com foco em:**
- ✨ Código limpo e organizado
- 📚 Documentação completa
- 🔒 Segurança
- 🚀 Performance
- 🛠️ Manutenibilidade
