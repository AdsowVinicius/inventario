# Controle de Acesso - PSCInventário

## 📊 Matriz de Acesso por Tela

| Tela/Funcionalidade | ADMIN | CONTROLADORIA | CONTADOR |
|---------------------|:-----:|:-------------:|:--------:|
| **🔐 Login** | ✅ | ✅ | ✅ |
| **📊 Dashboard** | ✅ | ❌ | ❌ |
| **📝 Contagem** | ✅ | ❌ | ✅ |
| **📋 Gestão de Contagens** | ✅ | ❌ | ❌ |
| **📦 Gestão de Itens** | ✅ | ❌ | ❌ |
| **📤 Exportação** | ✅ | ✅ | ❌ |
| **👥 Gestão de Usuários** | ✅ | ❌ | ❌ |

---

## 🔄 Redirecionamento Após Login

| Role | Página Inicial |
|------|----------------|
| **ADMIN** | `/dashboard` |
| **CONTROLADORIA** | `/exportacao` |
| **CONTADOR** | `/contagem` |

---

## 🔧 Permissões Detalhadas por Funcionalidade

### 📊 Dashboard (`/dashboard`)
| Ação | ADMIN | CONTROLADORIA | CONTADOR |
|------|:-----:|:-------------:|:--------:|
| Ver KPIs | ✅ | ❌ | ❌ |
| Ver Divergências | ✅ | ❌ | ❌ |
| Ver Progresso por Zona | ✅ | ❌ | ❌ |
| Filtrar por Planta | ✅ | ❌ | ❌ |

### 📝 Contagem (`/contagem`)
| Ação | ADMIN | CONTROLADORIA | CONTADOR |
|------|:-----:|:-------------:|:--------:|
| Realizar contagem | ✅ | ❌ | ✅ |
| Selecionar zona | ✅ | ❌ | ✅ |
| Selecionar nº contagem (1, 2, 3) | ✅ | ❌ | ✅ |
| Ver histórico da sessão | ✅ | ❌ | ✅ |

### 📋 Gestão de Contagens (`/gestao-contagens`)
| Ação | ADMIN | CONTROLADORIA | CONTADOR |
|------|:-----:|:-------------:|:--------:|
| Listar contagens | ✅ | ❌ | ❌ |
| Filtrar contagens | ✅ | ❌ | ❌ |
| Editar contagem | ✅ | ❌ | ❌ |
| Excluir contagem | ✅ | ❌ | ❌ |

### 📦 Gestão de Itens (`/itens`)
| Ação | ADMIN | CONTROLADORIA | CONTADOR |
|------|:-----:|:-------------:|:--------:|
| Listar itens | ✅ | ❌ | ❌ |
| Criar item | ✅ | ❌ | ❌ |
| Editar item | ✅ | ❌ | ❌ |
| Excluir item | ✅ | ❌ | ❌ |

### 📤 Exportação (`/exportacao`)
| Ação | ADMIN | CONTROLADORIA | CONTADOR |
|------|:-----:|:-------------:|:--------:|
| Ver preview | ✅ | ✅ | ❌ |
| Filtrar dados | ✅ | ✅ | ❌ |
| Exportar CSV | ✅ | ✅ | ❌ |
| Exportar Excel | ✅ | ✅ | ❌ |

### 👥 Gestão de Usuários (`/usuarios`)
| Ação | ADMIN | CONTROLADORIA | CONTADOR |
|------|:-----:|:-------------:|:--------:|
| Listar usuários | ✅ | ❌ | ❌ |
| Criar usuário | ✅ | ❌ | ❌ |
| Editar usuário | ✅ | ❌ | ❌ |
| Excluir usuário | ✅ | ❌ | ❌ |

---

## 📱 Menu de Navegação (Navbar)

| Item do Menu | ADMIN | CONTROLADORIA | CONTADOR |
|--------------|:-----:|:-------------:|:--------:|
| 📊 Dashboard | ✅ | ❌ | ❌ |
| 📝 Contagem | ✅ | ❌ | ✅ |
| 📋 Gestão | ✅ | ❌ | ❌ |
| 📦 Itens | ✅ | ❌ | ❌ |
| 📤 Exportar | ✅ | ✅ | ❌ |
| 👥 Usuários | ✅ | ❌ | ❌ |

---

## 🔒 Resumo por Role

### 👑 ADMIN (Administrador)
- **Acesso total** a todas as funcionalidades
- Único que pode: excluir itens, gerenciar usuários, editar/excluir contagens
- Página inicial: Dashboard

### 📊 CONTROLADORIA
- Foco em **exportação de dados**
- Pode exportar dados para análise
- **Não pode** fazer contagens, gerenciar itens nem acessar dashboard
- Página inicial: Exportação

### 📦 CONTADOR
- Foco em **realizar contagens**
- Acesso apenas à tela de contagem
- **Não pode** editar, excluir ou ver outras funcionalidades
- Página inicial: Contagem

---

## 📋 Campos Obrigatórios no Cadastro de Usuário

| Campo | Obrigatório | Validação |
|-------|:-----------:|-----------|
| User Name | ✅ | Mínimo 3 caracteres |
| Nome Completo | ✅ | Mínimo 3 caracteres |
| Departamento | ✅ | Mínimo 2 caracteres |
| Senha | ✅ | Mínimo 6 caracteres |
| Planta | ✅ | Seleção obrigatória |
| Email | ❌ | Formato válido (opcional) |

---

*Última atualização: 05/12/2025*
