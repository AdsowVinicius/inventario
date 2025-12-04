# Sistema de Inventário - Frontend

Interface web moderna desenvolvida com React e Vite para o sistema de inventário.

## 🚀 Tecnologias

- **React 18** - Biblioteca para interfaces
- **React Router DOM** - Roteamento
- **Axios** - Cliente HTTP
- **Vite** - Build tool e dev server
- **CSS3** - Estilização

## 📦 Instalação

### 1. Instalar dependências

```bash
npm install
```

ou

```bash
yarn install
```

## 🏃 Executar

### Modo desenvolvimento

```bash
npm run dev
```

ou

```bash
yarn dev
```

A aplicação estará disponível em: `http://localhost:3000`

### Build para produção

```bash
npm run build
```

ou

```bash
yarn build
```

### Preview da build

```bash
npm run preview
```

## 📚 Estrutura do Projeto

```
frontend/
├── src/
│   ├── index.jsx           # Ponto de entrada
│   ├── index.css           # Estilos globais
│   ├── pages/
│   │   ├── Login.jsx       # Tela de login
│   │   ├── Login.css
│   │   ├── Contagem.jsx    # Tela de contagem
│   │   ├── Contagem.css
│   │   ├── Exportacao.jsx  # Tela de exportação
│   │   └── Exportacao.css
│   ├── components/
│   │   ├── Navbar.jsx      # Barra de navegação
│   │   ├── Navbar.css
│   │   └── ProtectedRoute.jsx  # Proteção de rotas
│   └── services/
│       └── api.js          # Serviços da API
├── index.html              # HTML base
├── package.json            # Dependências
└── vite.config.js          # Configuração Vite
```

## 🔐 Autenticação

O sistema usa JWT armazenado no `localStorage`. Após o login, todas as requisições incluem automaticamente o token no header `Authorization`.

## 📱 Páginas

### Login (/)
- Autenticação de usuários
- Validação de credenciais
- Redirecionamento automático após login

### Contagem (/contagem)
- Disponível para todos os usuários autenticados
- Sugestão automática do número de contagem
- Seleção de part numbers dinâmica
- Validação de formulário

### Exportação (/exportacao)
- Disponível apenas para `admin` e `encarregado`
- Filtros opcionais
- Exportação CSV e Excel
- Download automático de arquivos

## 🎨 Features

- ✅ Interface 100% em PT-BR
- ✅ Design responsivo
- ✅ Validação de formulários
- ✅ Mensagens de feedback
- ✅ Proteção de rotas por papel
- ✅ Logout automático em caso de token inválido
- ✅ Navegação intuitiva

## 🔧 Configuração da API

Por padrão, o frontend conecta-se à API em `http://10.200.10.57:8000`.

Para alterar, edite o arquivo `src/services/api.js`:

```javascript
const API_BASE_URL = 'http://seu-servidor:porta';
```

## 📝 Licença

MIT
