"""
Script para importar itens do Excel PSCP para o banco de dados

ANTES DE EXECUTAR:
1. Verifique se o arquivo Excel está em: exel lista de materiais/materiais pscp.xlsx
2. O Excel deve ter as colunas de materiais (Material, Descrição, Planta, etc.)

3. Execute com: .\env\Scripts\python.exe importar_itens_pscp.py

OPÇÕES:
- Para limpar a tabela antes de importar, mude 'limpar_tabela_antes = True'
- Para apenas adicionar novos itens (sem duplicar), mantenha 'atualizar_existentes = True'
"""

import pandas as pd
import pymysql
from datetime import datetime

# ========== CONFIGURAÇÕES ==========
# Caminho do arquivo Excel PSCP
ARQUIVO_EXCEL = 'exel lista de materiais/materiais pscp.xlsx'

# Limpar tabela antes de importar? (CUIDADO: apaga todos os dados!)
limpar_tabela_antes = False

# Atualizar itens existentes? (se False, ignora duplicados)
atualizar_existentes = True

# Mostrar progresso a cada N itens
mostrar_progresso_cada = 500
# ===================================


def conectar_db():
    """Conecta ao banco de dados"""
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='inventario',
        charset='utf8mb4'
    )


def ler_excel():
    """Lê o arquivo Excel e retorna DataFrame"""
    print(f"\n{'='*60}")
    print(f"IMPORTAÇÃO DE MATERIAIS PSCP")
    print(f"{'='*60}")
    print(f"\n📖 Lendo arquivo Excel: {ARQUIVO_EXCEL}")
    
    try:
        df = pd.read_excel(ARQUIVO_EXCEL)
        print(f"   ✅ {len(df)} linhas encontradas")
        print(f"\n   📋 Colunas encontradas:")
        for i, col in enumerate(df.columns.tolist()):
            print(f"      {i+1}. '{col}'")
        return df
    except FileNotFoundError:
        print(f"   ❌ ERRO: Arquivo não encontrado!")
        print(f"   Verifique se o arquivo existe em: {ARQUIVO_EXCEL}")
        return None


def detectar_colunas(df):
    """Detecta automaticamente quais colunas usar"""
    print("\n🔍 Detectando colunas...")
    
    colunas_mapeadas = {
        'material': None,
        'descricao': None,
        'planta': None,
        'tipo': None,
        'und_medida': None,
        'deposito': None
    }
    
    # Padrões de nome de coluna para cada campo
    padroes = {
        'material': ['material', 'num_material', 'num_materiall', 'codigo', 'cod_material', 'part_number'],
        'descricao': ['descricao', 'txt_descrica_material', 'texto breve material', 'desc_material', 'nome'],
        'planta': ['planta', 'plant', 'centro'],
        'tipo': ['tipo', 'tipo_material', 'tipo de material', 'categoria'],
        'und_medida': ['und_medida', 'uni_medida', 'umb', 'unidade', 'um'],
        'deposito': ['deposito', 'dep', 'almoxarifado']
    }
    
    colunas_lower = {col.lower().strip(): col for col in df.columns}
    
    for campo, possiveis in padroes.items():
        for possivel in possiveis:
            for col_lower, col_original in colunas_lower.items():
                if possivel in col_lower:
                    colunas_mapeadas[campo] = col_original
                    break
            if colunas_mapeadas[campo]:
                break
    
    print("\n   📌 Mapeamento detectado:")
    for campo, coluna in colunas_mapeadas.items():
        status = "✅" if coluna else "⚠️  NÃO ENCONTRADA"
        print(f"      {campo}: {coluna if coluna else status}")
    
    return colunas_mapeadas


def preparar_dados(df, colunas):
    """Prepara os dados do DataFrame para inserção"""
    print("\n🔄 Preparando dados...")
    
    dados = []
    erros_linha = 0
    
    for idx, row in df.iterrows():
        try:
            # Material (obrigatório)
            material = ''
            if colunas['material'] and pd.notna(row[colunas['material']]):
                material = str(row[colunas['material']]).strip()
            
            if not material:
                erros_linha += 1
                continue
            
            # Descrição
            descricao = ''
            if colunas['descricao'] and pd.notna(row[colunas['descricao']]):
                descricao = str(row[colunas['descricao']]).strip()
            
            # Planta (obrigatório)
            planta = ''
            if colunas['planta'] and pd.notna(row[colunas['planta']]):
                planta = str(row[colunas['planta']]).strip()
            
            if not planta:
                erros_linha += 1
                continue
            
            # Tipo de material
            tipo = ''
            if colunas['tipo'] and pd.notna(row[colunas['tipo']]):
                tipo = str(row[colunas['tipo']]).strip()
            
            # Unidade de medida
            und_medida = ''
            if colunas['und_medida'] and pd.notna(row[colunas['und_medida']]):
                und_medida = str(row[colunas['und_medida']]).strip()
            
            # Depósito
            deposito = ''
            if colunas['deposito'] and pd.notna(row[colunas['deposito']]):
                deposito = str(row[colunas['deposito']]).strip()
            
            dados.append({
                'num_material': material[:50],
                'txt_descrica_material': descricao[:255] if descricao else None,
                'tipo_material': tipo[:50] if tipo else None,
                'planta': planta[:10] if planta else None,
                'und_medida': und_medida[:10] if und_medida else None,
                'deposito': deposito[:50] if deposito else None
            })
            
        except Exception as e:
            erros_linha += 1
            continue
    
    print(f"   ✅ {len(dados)} itens válidos preparados")
    if erros_linha > 0:
        print(f"   ⚠️  {erros_linha} linhas ignoradas (material ou planta vazio)")
    
    return dados


def importar_dados(dados):
    """Importa os dados para o banco"""
    connection = conectar_db()
    
    try:
        with connection.cursor() as cursor:
            # Limpar tabela se configurado
            if limpar_tabela_antes:
                print("\n🗑️  Limpando tabela itens_inventario...")
                cursor.execute("DELETE FROM itens_inventario")
                cursor.execute("ALTER TABLE itens_inventario AUTO_INCREMENT = 1")
                print("   ✅ Tabela limpa!")
            
            print(f"\n📥 Importando {len(dados)} itens...")
            
            inseridos = 0
            atualizados = 0
            ignorados = 0
            erros = 0
            
            for i, item in enumerate(dados):
                try:
                    # Verificar se já existe
                    cursor.execute(
                        "SELECT id FROM itens_inventario WHERE num_material = %s AND planta = %s",
                        (item['num_material'], item['planta'])
                    )
                    existente = cursor.fetchone()
                    
                    if existente:
                        if atualizar_existentes:
                            # Atualizar
                            cursor.execute("""
                                UPDATE itens_inventario 
                                SET txt_descrica_material = %s,
                                    tipo_material = %s,
                                    und_medida = %s,
                                    deposito = %s
                                WHERE num_material = %s AND planta = %s
                            """, (
                                item['txt_descrica_material'],
                                item['tipo_material'],
                                item['und_medida'],
                                item['deposito'],
                                item['num_material'],
                                item['planta']
                            ))
                            atualizados += 1
                        else:
                            ignorados += 1
                    else:
                        # Inserir novo
                        cursor.execute("""
                            INSERT INTO itens_inventario 
                            (num_material, txt_descrica_material, tipo_material, planta, und_medida, deposito)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (
                            item['num_material'],
                            item['txt_descrica_material'],
                            item['tipo_material'],
                            item['planta'],
                            item['und_medida'],
                            item['deposito']
                        ))
                        inseridos += 1
                    
                    # Mostrar progresso
                    if (i + 1) % mostrar_progresso_cada == 0:
                        print(f"   📊 Processados: {i + 1}/{len(dados)}")
                        
                except Exception as e:
                    erros += 1
                    if erros <= 5:
                        print(f"   ⚠️  Erro no item {item['num_material']}: {str(e)[:50]}")
            
            # Commit das alterações
            connection.commit()
            
            print(f"\n{'='*60}")
            print("📊 RESULTADO DA IMPORTAÇÃO")
            print(f"{'='*60}")
            print(f"   ✅ Inseridos:   {inseridos}")
            print(f"   🔄 Atualizados: {atualizados}")
            print(f"   ⏭️  Ignorados:  {ignorados}")
            print(f"   ❌ Erros:       {erros}")
            print(f"   📦 Total:       {inseridos + atualizados}")
            print(f"{'='*60}")
            
    except Exception as e:
        print(f"\n❌ ERRO GERAL: {e}")
        connection.rollback()
    finally:
        connection.close()


def verificar_preview(df, colunas):
    """Mostra preview dos dados antes de importar"""
    print("\n📋 PREVIEW DOS DADOS (primeiras 5 linhas):")
    print("-" * 80)
    
    for idx, row in df.head(5).iterrows():
        material = row[colunas['material']] if colunas['material'] and pd.notna(row[colunas['material']]) else '-'
        descricao = row[colunas['descricao']] if colunas['descricao'] and pd.notna(row[colunas['descricao']]) else '-'
        planta = row[colunas['planta']] if colunas['planta'] and pd.notna(row[colunas['planta']]) else '-'
        
        # Truncar descrição
        if len(str(descricao)) > 40:
            descricao = str(descricao)[:40] + "..."
        
        print(f"   {material} | {planta} | {descricao}")
    
    print("-" * 80)


def main():
    """Função principal"""
    # Ler arquivo Excel
    df = ler_excel()
    if df is None:
        return
    
    # Detectar colunas
    colunas = detectar_colunas(df)
    
    # Verificar se colunas obrigatórias foram encontradas
    if not colunas['material'] or not colunas['planta']:
        print("\n❌ ERRO: Colunas obrigatórias não encontradas!")
        print("   O arquivo precisa ter pelo menos:")
        print("   - Uma coluna de Material (código/número)")
        print("   - Uma coluna de Planta")
        return
    
    # Preview dos dados
    verificar_preview(df, colunas)
    
    # Confirmar importação
    print("\n" + "="*60)
    print("🚀 Iniciando importação automaticamente...")
    
    # Preparar e importar dados
    dados = preparar_dados(df, colunas)
    
    if dados:
        importar_dados(dados)
    else:
        print("\n❌ Nenhum dado válido para importar.")


if __name__ == "__main__":
    main()
