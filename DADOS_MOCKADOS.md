# 📋 Localização de Dados Mockados do Sistema

## 🎯 Índice Rápido

Este documento centraliza **TODOS** os locais onde há dados hardcoded no sistema para facilitar manutenção e customização.

---

## 🏭 1. PLANTAS

### 📍 Localizações:

#### **Backend:**
- **Arquivo:** `app/backend/models/user.py`
- **Linhas:** 6-14
- **Tipo:** Enum do SQLAlchemy

```python
class PlantaEnum(str, enum.Enum):
    """Enum para plantas"""
    PS01 = "PS01"
    PS02 = "PS02"
    PS03 = "PS03"
    PS05 = "PS05"
    PS09 = "PS09"
    PB82 = "PB82"
```

#### **Frontend - Contagem:**
- **Arquivo:** `app/frontend/src/pages/Contagem.jsx`
- **Linha:** 6
- **Tipo:** Array constante

```javascript
const PLANTAS = ['PS01', 'PS02', 'PS03', 'PS05', 'PS09', 'PB82'];
```

#### **Frontend - Exportação:**
- **Arquivo:** `app/frontend/src/pages/Exportacao.jsx`
- **Linha:** 6
- **Tipo:** Array constante

```javascript
const PLANTAS = ['PS01', 'PS02', 'PS03', 'PS05', 'PS09', 'PB82'];
```

#### **Frontend - Gestão de Usuários:**
- **Arquivo:** `app/frontend/src/pages/UserManagement.jsx`
- **Linha:** 6
- **Tipo:** Array constante

```javascript
const PLANTAS = ['PS01', 'PS02', 'PS03', 'PS05', 'PS09', 'PB82'];
```

#### **Banco de Dados:**
- **Arquivo:** `database_setup.sql`
- **Linha:** 20
- **Tipo:** Enum do MySQL

```sql
planta ENUM('PS01', 'PS02', 'PS03', 'PS05', 'PS09', 'PB82') NOT NULL,
```

### ✏️ Como Adicionar uma Nova Planta:

1. **Adicionar no Backend:**
   ```python
   # Em app/backend/models/user.py
   class PlantaEnum(str, enum.Enum):
       PS01 = "PS01"
       PS02 = "PS02"
       # ... outras plantas
       PS10 = "PS10"  # ← NOVA PLANTA
   ```

2. **Adicionar no Frontend (Contagem):**
   ```javascript
   // Em app/frontend/src/pages/Contagem.jsx (linha 6)
   const PLANTAS = ['PS01', 'PS02', 'PS03', 'PS05', 'PS09', 'PB82', 'PS10'];
   ```

3. **Adicionar no Frontend (Exportação):**
   ```javascript
   // Em app/frontend/src/pages/Exportacao.jsx (linha 6)
   const PLANTAS = ['PS01', 'PS02', 'PS03', 'PS05', 'PS09', 'PB82', 'PS10'];
   ```

5. **Atualizar Banco de Dados:**
   ```sql
   -- Executar no MySQL
   ALTER TABLE user_table 
   MODIFY COLUMN planta ENUM('PS01', 'PS02', 'PS03', 'PS05', 'PS09', 'PB82', 'PS10') NOT NULL;
   ```

6. **Configurar Zonas (ver seção abaixo)**
   -- Executar no MySQL
   ALTER TABLE user_table 
   MODIFY COLUMN planta ENUM('PS01', 'PS02', 'PS03', 'PS05', 'PS09', 'PB82', 'PS10') NOT NULL;
   ```

5. **Configurar Zonas (ver seção abaixo)**

---

## 🗺️ 2. ZONAS POR PLANTA

### 📍 Localização:

- **Arquivo:** `app/frontend/src/pages/Contagem.jsx`
- **Linhas:** 9-16
- **Tipo:** Objeto constante (mapa planta → array de zonas)

```javascript
const ZONAS_POR_PLANTA = {
  'PS01': ['ZONA-A', 'ZONA-B', 'ZONA-C', 'ZONA-D'],
  'PS02': ['ZONA-A', 'ZONA-B', 'ZONA-C'],
  'PS03': ['ZONA-A', 'ZONA-B'],
  'PS05': ['ZONA-A', 'ZONA-B', 'ZONA-C', 'ZONA-D', 'ZONA-E'],
  'PS09': ['ZONA-A', 'ZONA-B', 'ZONA-C'],
  'PB82': ['ZONA-A', 'ZONA-B']
};
```

### ✏️ Como Adicionar Zonas em uma Planta:

```javascript
// Adicionar mais zonas em PS01:
const ZONAS_POR_PLANTA = {
  'PS01': ['ZONA-A', 'ZONA-B', 'ZONA-C', 'ZONA-D', 'ZONA-E', 'ZONA-F'],
  // ... outras plantas
};
```

### ✏️ Como Adicionar uma Nova Planta com Zonas:

```javascript
const ZONAS_POR_PLANTA = {
  'PS01': ['ZONA-A', 'ZONA-B', 'ZONA-C', 'ZONA-D'],
  // ... outras plantas
  'PS10': ['ZONA-A', 'ZONA-B', 'ZONA-C']  // ← NOVA PLANTA
};
```

**⚠️ IMPORTANTE:** Sempre que adicionar uma planta nova, adicione também suas zonas aqui!

---

## 👥 3. ROLES (PAPÉIS DE USUÁRIO)

### 📍 Localizações:

#### **Backend - Model:**
- **Arquivo:** `app/backend/models/user.py`
- **Linhas:** 17-21
- **Tipo:** Enum do SQLAlchemy

```python
class RoleEnum(str, enum.Enum):
    """Enum para papéis de usuário"""
    ADMIN = "ADMIN"
    ENCARREGADO = "ENCARREGADO"
    CONTADOR = "CONTADOR"
```

#### **Backend - Validações de API:**
- **Arquivo:** `app/backend/api/exportacao.py`
- **Linhas:** 25, 102, 162
- **Uso:** Decoradores de permissão

```python
@router.get("/csv")
async def exportar_csv(
    current_user: User = Depends(require_role("ADMIN", "ENCARREGADO"))
):
```

#### **Frontend - Navbar:**
- **Arquivo:** `app/frontend/src/components/Navbar.jsx`
- **Linha:** 17
- **Uso:** Verificação de permissões

```javascript
const canExport = user.role === 'ADMIN' || user.role === 'ENCARREGADO';
```

#### **Frontend - Rotas:**
- **Arquivo:** `app/frontend/src/index.jsx`
- **Linha:** 36
- **Uso:** Proteção de rotas

```javascript
<ProtectedRoute allowedRoles={['ADMIN', 'ENCARREGADO']}>
  <Exportacao />
</ProtectedRoute>
```

#### **Banco de Dados:**
- **Arquivo:** `database_setup.sql`
- **Linha:** 21
- **Tipo:** Enum do MySQL

```sql
role ENUM('ADMIN', 'ENCARREGADO', 'CONTADOR') NOT NULL DEFAULT 'CONTADOR',
```

### 📊 Matriz de Permissões:

| Role        | Login | Contagem | Exportação | Gestão Usuários |
|-------------|-------|----------|------------|-----------------|
| CONTADOR    | ✅    | ✅       | ❌         | ❌              |
| ENCARREGADO | ✅    | ✅       | ✅         | ✅ (sua planta) |
| ADMIN       | ✅    | ✅       | ✅         | ✅ (todas)      |

### 🔐 Regras de Gestão de Usuários:

**ADMIN:**
- ✅ Ver todos os usuários de todas as plantas
- ✅ Criar usuários em qualquer planta
- ✅ Editar qualquer usuário (exceto ele mesmo para deleção)
- ✅ Deletar qualquer usuário (exceto ele mesmo)
- ✅ Criar outros ADMINs

**ENCARREGADO:**
- ✅ Ver apenas usuários de sua planta
- ✅ Criar usuários apenas em sua planta
- ✅ Editar usuários de sua planta (exceto ADMINs)
- ✅ Deletar usuários de sua planta (exceto ADMINs)
- ❌ NÃO pode criar ADMINs
- ❌ NÃO pode editar/deletar ADMINs
- ❌ NÃO pode mudar usuários para outra planta

### ✏️ Como Adicionar um Novo Role:

**⚠️ CUIDADO:** Adicionar roles envolve mudanças em vários arquivos!

1. **Backend Model:**
   ```python
   # Em app/backend/models/user.py
   class RoleEnum(str, enum.Enum):
       ADMIN = "ADMIN"
       ENCARREGADO = "ENCARREGADO"
       CONTADOR = "CONTADOR"
       SUPERVISOR = "SUPERVISOR"  # ← NOVO ROLE
   ```

2. **Banco de Dados:**
   ```sql
   ALTER TABLE user_table 
   MODIFY COLUMN role ENUM('ADMIN', 'ENCARREGADO', 'CONTADOR', 'SUPERVISOR') NOT NULL;
   ```

3. **Atualizar Validações de API** (onde aplicável)

4. **Atualizar Verificações Frontend** (onde aplicável)

---

## 🔐 4. USUÁRIO ADMIN PADRÃO

### 📍 Localizações:

#### **Script de Criação:**
- **Arquivo:** `app/backend/create_admin.py`
- **Linhas:** 25-30

```python
admin = User(
    user_name="admin",
    senha_hash=hash_password("admin123"),
    planta=PlantaEnum.PS01,
    role=RoleEnum.ADMIN
)
```

### 🔑 Credenciais Padrão:

- **Usuário:** `admin`
- **Senha:** `admin123`
- **Planta:** `PS01`
- **Role:** `ADMIN`

### ✏️ Como Alterar o Admin Padrão:

```python
# Em app/backend/create_admin.py
admin = User(
    user_name="superadmin",        # ← Novo nome
    senha_hash=hash_password("senha_forte_123"),  # ← Nova senha
    planta=PlantaEnum.PS05,        # ← Nova planta
    role=RoleEnum.ADMIN
)
```

---

## 📦 5. CAMPOS DO FORMULÁRIO DE CONTAGEM

### 📍 Localização:

- **Arquivo:** `app/frontend/src/pages/Contagem.jsx`
- **Linhas:** 23-29
- **Tipo:** Estado inicial do formulário

```javascript
const [formData, setFormData] = useState({
  num_contagem: 1,
  etiqueta_inventario: '',
  part_number: '',
  campo: '',
  qtd: 0
});
```

### 📝 Campos e Validações:

| Campo                 | Tipo    | Validação         | Obrigatório |
|-----------------------|---------|-------------------|-------------|
| num_contagem          | Number  | Inteiro positivo  | ✅          |
| etiqueta_inventario   | String  | Somente números   | ✅          |
| part_number           | String  | Somente números   | ✅          |
| campo                 | String  | Texto livre       | ❌          |
| qtd                   | Number  | Inteiro positivo  | ✅          |

---

## 🎨 6. CORES DO TEMA

### 📍 Localizações:

#### **CSS Global:**
- **Arquivo:** `app/frontend/src/index.css`
- **Variáveis CSS (se existirem)**

#### **CSS da Navbar:**
- **Arquivo:** `app/frontend/src/components/Navbar.css`

#### **CSS do Login:**
- **Arquivo:** `app/frontend/src/pages/Login.css`

#### **CSS da Contagem:**
- **Arquivo:** `app/frontend/src/pages/Contagem.css`

#### **CSS da Exportação:**
- **Arquivo:** `app/frontend/src/pages/Exportacao.css`

### 🎨 Paleta de Cores:

| Cor       | Código    | Uso                          |
|-----------|-----------|------------------------------|
| Branco    | #ffffff   | Background base              |
| Vermelho  | #dc3545   | Primary (botões, links)      |
| Vermelho  | #c82333   | Primary hover                |
| Cinza     | #6c757d   | Secondary (textos)           |
| Cinza     | #5a6268   | Secondary hover              |
| Cinza     | #f8f9fa   | Backgrounds secundários      |
| Verde     | #28a745   | Sucesso                      |
| Amarelo   | #ffc107   | Avisos                       |

### ✏️ Como Alterar as Cores:

Buscar e substituir nos arquivos CSS:
- `#dc3545` → Nova cor primária
- `#c82333` → Nova cor primária (hover)
- `#6c757d` → Nova cor secundária

---

## 🔌 7. URLs E CONFIGURAÇÕES DE API

### 📍 Localizações:

#### **Backend - CORS:**
- **Arquivo:** `app/backend/.env`
- **Linha:** FRONTEND_URL

```
FRONTEND_URL=http://localhost:3000
```

#### **Frontend - Base URL:**
- **Arquivo:** `app/frontend/src/services/api.js`
- **Constante baseURL**

```javascript
const api = axios.create({
  baseURL: 'http://localhost:8000'
});
```

### ✏️ Como Alterar URLs:

**Para Produção:**
```bash
# Backend .env
FRONTEND_URL=https://inventario.minhaempresa.com

# Frontend api.js
baseURL: 'https://api.inventario.minhaempresa.com'
```

---

## 🗄️ 8. CONFIGURAÇÃO DO BANCO DE DADOS

### 📍 Localização:

- **Arquivo:** `app/backend/.env`

```
DATABASE_URL=mysql+pymysql://root@localhost:3306/inventario
SECRET_KEY=sua_chave_secreta_super_segura_123456
JWT_ALGORITHM=HS256
```

### ✏️ Como Alterar Conexão do Banco:

```
# Para produção:
DATABASE_URL=mysql+pymysql://usuario:senha@servidor.com:3306/inventario
```

---

## 📊 9. MODELOS DE DADOS (SCHEMAS)

### 📍 Localizações:

#### **Itens de Inventário:**
- **Arquivo:** `app/backend/models/item_inventario.py`

#### **Formulário de Contagem:**
- **Arquivo:** `app/backend/models/forms_contagem.py`

#### **Usuário:**
- **Arquivo:** `app/backend/models/user.py`

**Ver estrutura completa em:** `VISAO_GERAL.md`

---

## 🚀 10. PORTAS DOS SERVIÇOS

### 📍 Configurações:

| Serviço  | Porta | Onde Configurar                                |
|----------|-------|------------------------------------------------|
| Backend  | 8000  | Comando uvicorn ou arquivo de configuração   |
| Frontend | 3000  | Vite config (`vite.config.js`)                |
| MySQL    | 3306  | Padrão do MySQL                                |

### ✏️ Como Alterar Portas:

**Backend:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8080  # ← Nova porta
```

**Frontend:**
```javascript
// Em vite.config.js
export default defineConfig({
  server: {
    port: 3001  // ← Nova porta
  }
});
```

---

## 🔍 11. FILTROS DE EXPORTAÇÃO

### 📍 Localização:

- **Arquivo:** `app/frontend/src/pages/Exportacao.jsx`
- **Estado inicial dos filtros**

```javascript
const [filtros, setFiltros] = useState({
  planta: '',
  zona_inventario: '',
  etiqueta_inventario: '',
  part_number: '',
  data_inicio: '',
  data_fim: ''
});
```

---

## 📱 12. CONFIGURAÇÕES MOBILE

### 📍 Localizações:

#### **Viewport:**
- **Arquivo:** `app/frontend/index.html`
- **Meta tag viewport**

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
```

#### **Breakpoints:**
- **Todos os arquivos CSS**
- **Media query:** `@media (max-width: 768px)`

#### **Tamanhos de Toque:**
- Mínimo: **48x48px** (padrão Apple HIG)
- Botões: **48-52px** de altura
- Inputs: **48px** de altura

**Ver mais em:** `MOBILE_OTIMIZACOES.md`

---

## 📝 CHECKLIST DE ATUALIZAÇÃO

Ao adicionar uma nova planta, você precisa atualizar:

- [ ] `app/backend/models/user.py` - PlantaEnum
- [ ] `app/frontend/src/pages/Contagem.jsx` - PLANTAS (linha 6)
- [ ] `app/frontend/src/pages/Contagem.jsx` - ZONAS_POR_PLANTA (linhas 9-16)
- [ ] `app/frontend/src/pages/Exportacao.jsx` - PLANTAS (linha 6)
- [ ] `app/frontend/src/pages/UserManagement.jsx` - PLANTAS (linha 6)
- [ ] `database_setup.sql` - Enum de plantas
- [ ] Banco de dados - ALTER TABLE (se já em produção)

---

## 🔗 DOCUMENTOS RELACIONADOS

- `README.md` - Visão geral do sistema
- `VISAO_GERAL.md` - Arquitetura detalhada
- `CONFIGURACAO_ZONAS.md` - Como configurar zonas
- `LEITORES_CODIGO_BARRAS.md` - Integração com scanners
- `MOBILE_OTIMIZACOES.md` - Otimizações mobile
- `COMANDOS_UTEIS.md` - Scripts e comandos úteis

---

## 💡 DICAS IMPORTANTES

1. **Sempre mantenha Backend e Frontend sincronizados** - Se mudar no backend, mude no frontend
2. **Teste após mudanças** - Principalmente enums do banco de dados
3. **Documente customizações** - Adicione comentários quando fizer alterações
4. **Backup antes de ALTER TABLE** - Mudanças em enum do MySQL podem ser perigosas
5. **Use o padrão existente** - Mantenha o formato dos nomes (ex: PS01, ZONA-A)

---

**Última Atualização:** Dezembro 2025
**Versão do Documento:** 1.0
