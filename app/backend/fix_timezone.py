"""
Script para corrigir o fuso horário dos registros antigos na tabela forms_contagem

Os registros foram salvos em UTC e precisam ser ajustados para Brasília (UTC-3).
Este script subtrai 3 horas de todos os registros existentes.

Execute com: .\env\Scripts\python.exe fix_timezone.py
"""

import pymysql
from datetime import timedelta

def main():
    print("=" * 70)
    print("CORREÇÃO DE FUSO HORÁRIO - UTC para Brasília (UTC-3)")
    print("=" * 70)
    
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='inventario',
        charset='utf8mb4'
    )
    
    cursor = conn.cursor()
    
    try:
        # Verificar quantos registros existem
        cursor.execute("SELECT COUNT(*) FROM forms_contagem")
        total = cursor.fetchone()[0]
        print(f"\n[INFO] Total de registros na tabela: {total}")
        
        if total == 0:
            print("[INFO] Nenhum registro para corrigir.")
            return
        
        # Mostrar exemplo antes da correção
        cursor.execute("""
            SELECT id, timestamp, updated_at 
            FROM forms_contagem 
            ORDER BY id DESC 
            LIMIT 3
        """)
        print("\n[ANTES] Últimos 3 registros:")
        for row in cursor.fetchall():
            print(f"  ID {row[0]}: timestamp={row[1]}, updated_at={row[2]}")
        
        # Confirmar antes de executar
        resposta = input("\n⚠️  Deseja subtrair 3 horas de TODOS os registros? (s/n): ")
        if resposta.lower() != 's':
            print("\n[CANCELADO] Nenhuma alteração foi feita.")
            return
        
        # Atualizar timestamp (subtrair 3 horas = UTC para Brasília)
        cursor.execute("""
            UPDATE forms_contagem 
            SET timestamp = DATE_SUB(timestamp, INTERVAL 3 HOUR),
                updated_at = DATE_SUB(updated_at, INTERVAL 3 HOUR)
        """)
        
        registros_atualizados = cursor.rowcount
        conn.commit()
        
        print(f"\n[OK] {registros_atualizados} registros atualizados com sucesso!")
        
        # Mostrar exemplo depois da correção
        cursor.execute("""
            SELECT id, timestamp, updated_at 
            FROM forms_contagem 
            ORDER BY id DESC 
            LIMIT 3
        """)
        print("\n[DEPOIS] Últimos 3 registros:")
        for row in cursor.fetchall():
            print(f"  ID {row[0]}: timestamp={row[1]}, updated_at={row[2]}")
            
    except Exception as e:
        print(f"\n[ERRO] {e}")
        conn.rollback()
    finally:
        conn.close()
    
    print("\n" + "=" * 70)
    print("CONCLUÍDO!")
    print("=" * 70)


if __name__ == "__main__":
    main()
