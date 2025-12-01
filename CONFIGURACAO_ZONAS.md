# 🗺️ Configuração de Zonas por Planta

## 📋 Zonas Cadastradas

Este documento descreve as zonas de inventário configuradas para cada planta.

### **PS01**
- ZONA-A
- ZONA-B
- ZONA-C
- ZONA-D

### **PS02**
- ZONA-A
- ZONA-B
- ZONA-C

### **PS03**
- ZONA-A
- ZONA-B

### **PS05**
- ZONA-A
- ZONA-B
- ZONA-C
- ZONA-D
- ZONA-E

### **PS09**
- ZONA-A
- ZONA-B
- ZONA-C

### **PB82**
- ZONA-A
- ZONA-B

---

## ⚙️ Como Adicionar ou Modificar Zonas

Para adicionar ou modificar zonas, edite o arquivo:
```
app/frontend/src/pages/Contagem.jsx
```

Localize a constante `ZONAS_POR_PLANTA` e modifique conforme necessário:

```javascript
const ZONAS_POR_PLANTA = {
  'PS01': ['ZONA-A', 'ZONA-B', 'ZONA-C', 'ZONA-D'],
  'PS02': ['ZONA-A', 'ZONA-B', 'ZONA-C'],
  // ... adicione ou modifique aqui
};
```

### Exemplos de Modificação:

**Adicionar nova zona em PS01:**
```javascript
'PS01': ['ZONA-A', 'ZONA-B', 'ZONA-C', 'ZONA-D', 'ZONA-E'],
```

**Adicionar nova planta:**
```javascript
'PS10': ['ZONA-A', 'ZONA-B'],
```

**Usar nomenclatura diferente:**
```javascript
'PS01': ['ALMOXARIFADO-1', 'ALMOXARIFADO-2', 'PRODUCAO-A'],
```

---

## 🔄 Comportamento do Sistema

1. **Seleção de Planta**: Ao selecionar uma planta, apenas as zonas daquela planta são exibidas
2. **Mudança de Planta**: Ao mudar de planta, o campo de zona é limpo automaticamente
3. **Validação**: O usuário só pode selecionar zonas predefinidas
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
