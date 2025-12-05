"""
Script para importar itens do Excel para o banco de dados

ANTES DE EXECUTAR:
1. Verifique se o arquivo Excel está em: exel lista de materiais/materiais psca.xlsx
2. O Excel deve ter as colunas:
   - Material (será convertido para num_material / part_number)
   - Texto breve material (será convertido para txt_descrica_material / descricao)
   - Tipo de material (será convertido para tipo_material)
   - Planta (será mantido como planta)
   - UMB (será convertido para und_medida)

3. Execute com: .\env\Scripts\python.exe importar_itens_excel.py

OPÇÕES:
- Para limpar a tabela antes de importar, descomente a linha 'limpar_tabela_antes = True'
- Para apenas adicionar novos itens (sem duplicar), mantenha 'atualizar_existentes = True'
"""

import pandas as pd
import pymysql
from datetime import datetime

# ========== CONFIGURAÇÕES ==========
# Caminho do arquivo Excel
ARQUIVO_EXCEL = 'exel lista de materiais/materiais psca.xlsx'

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
    print(f"📖 Lendo arquivo Excel: {ARQUIVO_EXCEL}")
    df = pd.read_excel(ARQUIVO_EXCEL)
    print(f"   ✅ {len(df)} linhas encontradas")
    print(f"   📋 Colunas: {df.columns.tolist()}")
    return df


def preparar_dados(df):
    """Prepara os dados do DataFrame para inserção"""
    print("\n🔄 Preparando dados...")
    
    # Mapear colunas do Excel para colunas do banco
    # Excel atual: num_materiall, txt_descrica_material, planta, deposito, tipo_material, uni_medida
    # Banco: num_material, txt_descrica_material, tipo_material, planta, und_medida
    
    dados = []
    for idx, row in df.iterrows():
        # Converter Material para string e remover zeros à esquerda se necessário
        # Tentar diferentes nomes de coluna para compatibilidade
        material = None
        for col in ['num_materiall', 'num_material', 'Material']:
            if col in df.columns:
                material = str(row[col]).strip() if pd.notna(row[col]) else ''
                break
        
        if not material:
            continue
        
        # Texto breve / descrição
        descricao = None
        for col in ['txt_descrica_material', 'Texto breve material', 'descricao']:
            if col in df.columns:
                descricao = str(row[col]).strip() if pd.notna(row[col]) else ''
                break
        
        # Tipo de material
        tipo = None
        for col in ['tipo_material', 'Tipo de material']:
            if col in df.columns:
                tipo = str(row[col]).strip() if pd.notna(row[col]) else ''
                break
        
        # Planta
        planta = None
        for col in ['planta', 'Planta']:
            if col in df.columns:
                planta = str(row[col]).strip() if pd.notna(row[col]) else ''
                break
        
        # Unidade de medida
        und_medida = None
        for col in ['uni_medida', 'und_medida', 'UMB']:
            if col in df.columns:
                und_medida = str(row[col]).strip() if pd.notna(row[col]) else ''
                break
        
        # Depósito
        deposito = None
        for col in ['deposito', 'Deposito']:
            if col in df.columns:
                deposito = str(row[col]).strip() if pd.notna(row[col]) else ''
                break
        
        # Ignorar linhas sem material ou planta
        if not material or not planta:
            continue
        
        dados.append({
            'num_material': material,
            'txt_descrica_material': descricao[:255] if descricao else None,  # Limitar a 255 caracteres
            'tipo_material': tipo[:50] if tipo else None,
            'planta': planta[:10] if planta else None,
            'und_medida': und_medida[:10] if und_medida else None,
            'deposito': deposito[:20] if deposito else None
        })
    
    print(f"   ✅ {len(dados)} itens válidos preparados")
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
                                    und_medida = %s
                                WHERE num_material = %s AND planta = %s
                            """, (
                                item['txt_descrica_material'],
                                item['tipo_material'],
                                item['und_medida'],
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
                    if erros <= 5:  # Mostrar apenas os primeiros 5 erros
                        print(f"   ⚠️  Erro no item {item['num_material']}: {e}")
            
            connection.commit()
            
            print(f"\n✅ Importação concluída!")
            print(f"   📊 Inseridos: {inseridos}")
            print(f"   📊 Atualizados: {atualizados}")
            print(f"   📊 Ignorados: {ignorados}")
            if erros > 0:
                print(f"   ⚠️  Erros: {erros}")
            
    except Exception as e:
        print(f"\n❌ Erro na importação: {e}")
        connection.rollback()
        raise
    finally:
        connection.close()


def mostrar_resumo():
    """Mostra resumo dos dados no banco"""
    connection = conectar_db()
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM itens_inventario")
            total = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT planta, COUNT(*) as qtd 
                FROM itens_inventario 
                GROUP BY planta 
                ORDER BY planta
            """)
            por_planta = cursor.fetchall()
            
            print(f"\n📊 RESUMO DO BANCO DE DADOS:")
            print(f"   Total de itens: {total}")
            print(f"   Por planta:")
            for planta, qtd in por_planta:
                print(f"      - {planta}: {qtd} itens")
                
    finally:
        connection.close()


if __name__ == "__main__":
    print("=" * 60)
    print("   IMPORTADOR DE ITENS DO EXCEL")
    print("=" * 60)
    print(f"   Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)
    
    # Ler Excel
    df = ler_excel()
    
    # Preparar dados
    dados = preparar_dados(df)
    
    # Confirmar importação
    print("\n" + "=" * 60)
    print("⚠️  ATENÇÃO!")
    print(f"   - Limpar tabela antes: {'SIM' if limpar_tabela_antes else 'NÃO'}")
    print(f"   - Atualizar existentes: {'SIM' if atualizar_existentes else 'NÃO'}")
    print("=" * 60)
    
    resposta = input("\n🤔 Deseja continuar com a importação? (s/n): ")
    
    if resposta.lower() in ['s', 'sim', 'y', 'yes']:
        importar_dados(dados)
        mostrar_resumo()
    else:
        print("\n❌ Importação cancelada pelo usuário.")
