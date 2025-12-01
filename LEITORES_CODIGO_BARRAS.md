# 📱 Integração com Leitores de Código de Barras

## 🎯 Configuração dos Coletores

O sistema está preparado para receber entrada de leitores de código de barras (coletoras) no campo **Part Number**.

### ✅ Funcionalidades Implementadas

1. **Campo de texto livre** - Aceita entrada digitada ou escaneada
2. **Autocompletar** - Sugere códigos existentes conforme digitação
3. **Foco automático** - Após escanear, pode pressionar Tab para avançar
4. **Validação** - Verifica se o código existe no sistema

### 🔧 Configuração do Leitor

**Configurações Recomendadas para o Leitor:**

1. **Modo de Operação:** HID (Human Interface Device)
   - O leitor deve simular um teclado
   - Cada leitura deve enviar o código + ENTER ou TAB

2. **Sufixo após leitura:**
   - Configure para enviar TAB após cada código
   - Isso permite avançar automaticamente para o próximo campo
   - Alternativa: ENTER (mas pode submeter o formulário)

3. **Prefixo (opcional):**
   - Não é necessário adicionar prefixo
   - O sistema aceita apenas o número do material

### 📋 Fluxo de Uso com Coletora

1. Usuário abre a tela de **Contagem**
2. Preenche **Planta**, **Número da Contagem**, **Zona** e **Etiqueta**
3. **Posiciona o cursor no campo Part Number**
4. **Escaneia o código de barras** do material
5. O código é inserido automaticamente
6. Se configurado com TAB, avança para o campo **Quantidade**
7. Digita a quantidade
8. Clica em **Salvar Contagem**

### 🔍 Validação de Códigos

O sistema valida se o código existe na base de dados:
- ✅ **Código válido:** Permite salvar a contagem
- ❌ **Código inválido:** Exibe erro ao tentar salvar

### 📊 Formato do Código

- **Campo aceito:** `num_material` da tabela `itens_inventario`
- **Formato:** Texto livre (alfanumérico)
- **Exemplo:** `MAT-001`, `12345`, `ABC-XYZ-789`

### 🖥️ Testando a Integração

**Teste sem leitor:**
1. Acesse a tela de Contagem
2. Digite manualmente no campo Part Number
3. Observe o autocompletar funcionando

**Teste com leitor:**
1. Configure o leitor em modo HID
2. Coloque o foco no campo Part Number
3. Escaneie um código de barras
4. Verifique se o código aparece no campo

### ⚙️ Configuração Técnica do Leitor

**Parâmetros Datalogic/Zebra/Honeywell:**

```
Modo: USB HID / Keyboard Wedge
Sufixo: TAB (0x09) ou ENTER (0x0D)
Prefixo: Nenhum
Encoding: UTF-8
Auto-submit: Desabilitado
```

### 🔗 Integração com Sistema Web

O leitor deve estar configurado para:
1. Enviar dados como se fosse um teclado
2. Funcionar em navegadores web (Chrome, Edge, Firefox)
3. Não requer instalação de drivers adicionais
4. Compatível com Windows, Linux, macOS

### 📞 Suporte

Se o leitor não estiver funcionando:
1. Verifique se está em modo HID/Keyboard
2. Teste em um editor de texto (Notepad)
3. Confirme se envia o sufixo correto
4. Verifique se o foco está no campo correto

### 🎯 Atalhos de Teclado

- **TAB** - Avança para próximo campo
- **SHIFT + TAB** - Volta para campo anterior
- **ENTER** - Salva o formulário (se todos os campos estiverem preenchidos)

---

## 📦 Dados de Exemplo

Para testar, utilize os códigos de exemplo inseridos no banco:
- `MAT-001` - Material Teste 1
- `MAT-002` - Material Teste 2
- `MAT-003` - Material Teste 3
- `MAT-004` - Material Teste 4

Para adicionar mais materiais, use o script SQL ou interface de administração.
