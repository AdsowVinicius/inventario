"""
Script para adicionar coluna bloqueado_permanente na tabela user_table

Execute com: .\env\Scripts\python.exe add_bloqueado_column.py
"""

import pymysql

def main():
    print("=" * 60)
    print("ADICIONAR COLUNA bloqueado_permanente")
    print("=" * 60)
    
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='inventario',
        charset='utf8mb4'
    )
    
    cursor = conn.cursor()
    
    try:
        # Verificar se coluna já existe
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'inventario' 
            AND TABLE_NAME = 'user_table' 
            AND COLUMN_NAME = 'bloqueado_permanente'
        """)
        
        if cursor.fetchone()[0] > 0:
            print("\n[OK] Coluna 'bloqueado_permanente' já existe!")
        else:
            # Adicionar coluna
            cursor.execute("""
                ALTER TABLE user_table 
                ADD COLUMN bloqueado_permanente BOOLEAN NOT NULL DEFAULT FALSE
            """)
            conn.commit()
            print("\n[OK] Coluna 'bloqueado_permanente' adicionada com sucesso!")
        
        # Verificar estrutura
        cursor.execute("DESCRIBE user_table")
        print("\nEstrutura atual da tabela:")
        for row in cursor.fetchall():
            print(f"  - {row[0]}: {row[1]}")
            
    except Exception as e:
        print(f"\n[ERRO] {e}")
        conn.rollback()
    finally:
        conn.close()
    
    print("\n" + "=" * 60)
    print("CONCLUIDO!")
    print("=" * 60)


if __name__ == "__main__":
    main()
