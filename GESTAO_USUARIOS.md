# 👥 Gestão de Usuários - Sistema de Inventário

## 📋 Visão Geral

O sistema agora possui um módulo completo de gestão de usuários com controle de permissões baseado em roles e plantas.

---

## 🔐 Níveis de Acesso

### **ADMIN (Administrador)**
✅ **Permissões Totais:**
- Ver **todos** os usuários de **todas** as plantas
- Criar usuários em **qualquer planta**
- Editar **qualquer usuário**
- Deletar **qualquer usuário** (exceto ele mesmo)
- Criar outros **ADMINs**
- Atribuir **qualquer role** a usuários

### **ENCARREGADO**
⚠️ **Permissões Limitadas à Sua Planta:**
- Ver **apenas** usuários da **sua planta**
- Criar usuários **apenas** na **sua planta**
- Editar usuários da sua planta (❌ **exceto ADMINs**)
- Deletar usuários da sua planta (❌ **exceto ADMINs**)
- ❌ **NÃO pode** criar ADMINs
- ❌ **NÃO pode** editar ou deletar ADMINs
- ❌ **NÃO pode** mover usuários para outra planta
- Pode criar: **CONTADOR** e **ENCARREGADO**

### **CONTADOR**
❌ **Sem Acesso:**
- Não tem acesso à gestão de usuários

---

## 📍 Localização dos Arquivos

### **Backend:**
- **API:** `app/backend/api/users.py`
- **Schemas:** `app/backend/schemas/user.py` (adicionado `UserUpdate`)
- **Rotas:** Registrado em `app/backend/main.py`

### **Frontend:**
- **Componente:** `app/frontend/src/pages/UserManagement.jsx`
- **CSS:** `app/frontend/src/pages/UserManagement.css`
- **Rota:** Registrada em `app/frontend/src/index.jsx`
- **Menu:** Link adicionado em `app/frontend/src/components/Navbar.jsx`

---

## 🛣️ Endpoints da API

### **GET `/users/`**
Lista usuários conforme permissão:
- **ADMIN:** Retorna todos os usuários
- **ENCARREGADO:** Retorna apenas usuários da sua planta

**Headers:**
```
Authorization: Bearer {token}
```

**Response:**
```json
[
  {
    "id": 1,
    "user_name": "joao",
    "planta": "PS01",
    "role": "CONTADOR"
  }
]
```

---

### **GET `/users/{user_id}`**
Obter um usuário específico

**Validações:**
- ENCARREGADO só pode ver usuários de sua planta

---

### **POST `/users/`**
Criar novo usuário

**Body:**
```json
{
  "user_name": "novo_usuario",
  "senha": "senha123",
  "planta": "PS01",
  "role": "CONTADOR"
}
```

**Validações:**
- Username único
- ENCARREGADO só pode criar em sua planta
- ENCARREGADO não pode criar role ADMIN
- Senha mínima: 6 caracteres

---

### **PUT `/users/{user_id}`**
Atualizar usuário

**Body:** (todos os campos opcionais)
```json
{
  "user_name": "novo_nome",
  "senha": "nova_senha",
  "planta": "PS02",
  "role": "ENCARREGADO"
}
```

**Validações:**
- ENCARREGADO só pode editar usuários de sua planta
- ENCARREGADO não pode editar ADMINs
- ENCARREGADO não pode promover para ADMIN
- ENCARREGADO não pode mudar planta
- Se senha vazia, não altera senha

---

### **DELETE `/users/{user_id}`**
Deletar usuário

**Validações:**
- Usuário não pode deletar a si mesmo
- ENCARREGADO só pode deletar de sua planta
- ENCARREGADO não pode deletar ADMINs

---

## 🎨 Interface do Usuário

### **Tela Principal**
- Tabela responsiva com todos os usuários
- Colunas: Usuário, Planta, Perfil, Ações
- Badges coloridos por role:
  - 🔴 **ADMIN** - Vermelho
  - 🟡 **ENCARREGADO** - Amarelo
  - ⚫ **CONTADOR** - Cinza

### **Botão "Novo Usuário"**
Abre modal para criação

### **Ações por Usuário**
- **Editar:** Abre modal de edição
- **Deletar:** Confirma e remove usuário
- Botões aparecem apenas se usuário tem permissão

---

## 📱 Modal de Criação/Edição

### **Campos:**

1. **Nome de Usuário** *
   - Mínimo 3 caracteres
   - Único no sistema
   
2. **Senha** *
   - Mínimo 6 caracteres
   - Na edição: opcional (deixe vazio para não alterar)
   
3. **Planta** *
   - Dropdown com todas as plantas
   - 🔒 **ENCARREGADO:** Campo bloqueado na sua planta
   
4. **Perfil** *
   - CONTADOR
   - ENCARREGADO
   - ADMIN (apenas para ADMIN criar)

### **Botões:**
- **Cancelar:** Fecha modal sem salvar
- **Salvar:** Valida e salva usuário

---

## 🎯 Fluxo de Uso

### **Como ADMIN:**

1. Acesse menu **👥 Usuários**
2. Veja lista de **todos** os usuários
3. Clique **+ Novo Usuário**
4. Preencha:
   - Nome de usuário
   - Senha
   - Selecione **qualquer planta**
   - Selecione **qualquer role** (incluindo ADMIN)
5. Clique **Salvar**
6. ✅ Usuário criado!

### **Como ENCARREGADO:**

1. Acesse menu **👥 Usuários**
2. Veja apenas usuários da **sua planta**
3. Clique **+ Novo Usuário**
4. Preencha:
   - Nome de usuário
   - Senha
   - Planta: **fixo na sua planta** (não pode mudar)
   - Role: **CONTADOR** ou **ENCARREGADO** (ADMIN não aparece)
5. Clique **Salvar**
6. ✅ Usuário criado na sua planta!

---

## ⚠️ Regras de Segurança

### **Proteções Implementadas:**

1. ✅ **Autenticação obrigatória** - Token JWT em todos os endpoints
2. ✅ **Validação de role** - Apenas ADMIN e ENCARREGADO acessam
3. ✅ **Isolamento por planta** - ENCARREGADO só vê/edita sua planta
4. ✅ **Proteção de ADMIN** - ENCARREGADO não pode tocar em ADMINs
5. ✅ **Auto-proteção** - Usuário não pode deletar a si mesmo
6. ✅ **Username único** - Sistema valida duplicatas
7. ✅ **Senhas hash** - Armazenadas com bcrypt
8. ✅ **Validação de inputs** - Frontend e backend validam dados

---

## 🔧 Como Adicionar Permissões Customizadas

### **Exemplo: ENCARREGADO pode criar apenas CONTADORs**

Edite `app/backend/api/users.py`, função `criar_usuario`:

```python
# Após linha 95
if current_user.role == "ENCARREGADO":
    # Não pode criar ENCARREGADO nem ADMIN
    if user_data.role in ["ADMIN", "ENCARREGADO"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode criar usuários CONTADOR"
        )
```

E no frontend `UserManagement.jsx`:

```javascript
// Após linha 303
{ROLES.map(role => {
  // ENCARREGADO só vê CONTADOR
  if (currentUser.role === 'ENCARREGADO' && role.value !== 'CONTADOR') {
    return null;
  }
  return ...
})}
```

---

## 🐛 Troubleshooting

### **Erro 403 ao acessar /usuarios**
- Verifique que seu usuário é ADMIN ou ENCARREGADO
- Confirme que token JWT está válido no localStorage

### **Não consigo criar usuário ADMIN**
- Você é ENCARREGADO? Só ADMIN pode criar ADMIN
- Role está correto no token?

### **Dropdown planta está desabilitado**
- Você é ENCARREGADO? Planta fica travada na sua
- Comportamento esperado!

### **Erro ao deletar usuário**
- Você está tentando deletar você mesmo? ❌ Não permitido
- ENCARREGADO tentando deletar ADMIN? ❌ Não permitido
- Usuário de outra planta? ❌ ENCARREGADO só sua planta

---

## 📊 Dados Mockados

### **Roles:**
```javascript
const ROLES = [
  { value: 'CONTADOR', label: 'Contador' },
  { value: 'ENCARREGADO', label: 'Encarregado' },
  { value: 'ADMIN', label: 'Administrador' }
];
```

**Localização:** `app/frontend/src/pages/UserManagement.jsx` (linha 7-11)

### **Plantas:**
```javascript
const PLANTAS = ['PS01', 'PS02', 'PS03', 'PS05', 'PS09', 'PB82'];
```

**Localização:** `app/frontend/src/pages/UserManagement.jsx` (linha 6)

---

## 🎨 Estilos Mobile

A interface de gestão de usuários é **totalmente responsiva**:

- ✅ Tabela com scroll horizontal em mobile
- ✅ Modal adaptável para telas pequenas
- ✅ Botões com tamanho mínimo 48x48px (touch-friendly)
- ✅ Inputs com altura mínima 48px
- ✅ Font-size 16px (evita zoom no iOS)

**Breakpoint:** `@media (max-width: 768px)`

---

## 📚 Documentos Relacionados

- `DADOS_MOCKADOS.md` - Onde alterar plantas e roles
- `README.md` - Visão geral do sistema
- `VISAO_GERAL.md` - Arquitetura completa
- `MOBILE_OTIMIZACOES.md` - Otimizações mobile

---

## ✅ Checklist de Implementação

- [x] Endpoint GET /users/ (listar)
- [x] Endpoint GET /users/{id} (obter)
- [x] Endpoint POST /users/ (criar)
- [x] Endpoint PUT /users/{id} (editar)
- [x] Endpoint DELETE /users/{id} (deletar)
- [x] Schema UserUpdate no backend
- [x] Componente UserManagement.jsx
- [x] Estilos UserManagement.css
- [x] Rota protegida /usuarios
- [x] Link no menu navbar
- [x] Validações de permissão (ADMIN/ENCARREGADO)
- [x] Isolamento por planta
- [x] Proteção contra criar/editar ADMINs
- [x] Modal de criação/edição
- [x] Confirmação de deleção
- [x] Interface responsiva mobile
- [x] Documentação completa

---

**Status:** ✅ **COMPLETO E FUNCIONAL**

**Última Atualização:** Dezembro 2025
