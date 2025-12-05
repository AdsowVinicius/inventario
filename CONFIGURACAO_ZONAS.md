# 🗺️ Configuração de Zonas por Planta

## 📋 Zonas Cadastradas

Este documento descreve as zonas de inventário configuradas para cada planta.

### **PS01**
| Zona | Descrição |
|:----:|-----------|
| A | Acabado |
| B | Semi-Acabado |
| C | Matéria-Prima/Embalagens |
| D | Almoxarifado |
| E | Almox/Manutenção |
| F | Câmara-Fria |
| G | Qualidade |
| H | Engenharia |

### **PS02**
| Zona | Descrição |
|:----:|-----------|
| A | G2 |
| B | Qualidade |
| C | Sala de Tintas |
| D | Almoxarifado de Tintas |
| E | Almoxarifado |
| F | Almox/Manutenção |
| G | Polimento/Retoque |
| H | Montagem |
| I | Estoque Acabado |

### **PS03**
| Zona | Descrição |
|:----:|-----------|
| A | Acabado |
| B | Semi-Acabado |
| C | Componentes/Embalagens |
| D | Sala de Tintas |
| E | Almoxarifado |

### **PS05**
| Zona | Descrição |
|:----:|-----------|
| A | Almoxarifado |
| B | Estoque Acabado |
| C | Montagem |
| D | Colagem |
| E | Semi-Acabado |
| F | Sala de Materiais |
| G | G2 |
| H | Obsoleto |
| I | Engenharia/Qualidade |

### **PB82**
| Zona | Descrição |
|:----:|-----------|
| A | Almoxarifado |
| B | Estoque |
| C | Produção |

---

## ⚙️ Como Adicionar ou Modificar Zonas

Para adicionar ou modificar zonas, edite os arquivos:

**Backend:**
```
app/backend/api/exportacao.py
```

**Frontend:**
```
app/frontend/src/pages/Contagem.jsx
```

Localize a constante `ZONAS_POR_PLANTA` e modifique conforme necessário:

```javascript
const ZONAS_POR_PLANTA = {
  'PS01': [
    { codigo: 'A', descricao: 'Acabado' },
    { codigo: 'B', descricao: 'Semi-Acabado' },
    // ... adicione ou modifique aqui
  ],
};
```

---

## 🔄 Comportamento do Sistema

1. **Seleção de Planta**: Ao selecionar uma planta, apenas as zonas daquela planta são exibidas
2. **Mudança de Planta**: Ao mudar de planta, o campo de zona é limpo automaticamente
3. **Validação**: O usuário só pode selecionar zonas predefinidas
4. **Exportação**: A zona é exportada no formato "Zona (A) - Descrição"

---

*Última atualização: 05/12/2025*
4. **Consistência**: Garante que apenas zonas válidas sejam registradas no banco de dados

---

## 📝 Notas Importantes

- As zonas são armazenadas no frontend como dropdown
- Facilita a padronização e evita erros de digitação
- Cada planta pode ter quantas zonas forem necessárias
- Os nomes das zonas são case-sensitive (ZONA-A ≠ zona-a)

---

## 🔍 Exemplo de Uso

1. Usuário acessa a tela de contagem
2. Seleciona **Planta: PS01**
3. Vê as opções: ZONA-A, ZONA-B, ZONA-C, ZONA-D
4. Seleciona **ZONA-B**
5. Inicia as contagens naquela zona
6. Se precisar mudar para PS02, verá outras zonas: ZONA-A, ZONA-B, ZONA-C

---

## 💡 Dica para Gestão

Para facilitar a manutenção, considere criar um arquivo de configuração separado:

```javascript
// config/zonas.js
export const ZONAS_POR_PLANTA = {
  // configurações aqui
};
```

Assim fica mais fácil gerenciar as zonas sem mexer no código principal.
