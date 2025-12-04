"""
Script para adicionar campos nome_completo e departamento à tabela user_table
"""
import pymysql

def add_user_fields():
    """Adiciona colunas nome_completo e departamento"""
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='inventario',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # Verificar se coluna nome_completo existe
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.columns 
                WHERE table_schema = 'inventario' 
                AND table_name = 'user_table' 
                AND column_name = 'nome_completo'
            """)
            if cursor.fetchone()[0] == 0:
                print("Adicionando coluna 'nome_completo'...")
                cursor.execute("""
                    ALTER TABLE user_table 
                    ADD COLUMN nome_completo VARCHAR(60) NULL AFTER email
                """)
                print("✅ Coluna 'nome_completo' adicionada!")
            else:
                print("ℹ️ Coluna 'nome_completo' já existe.")
            
            # Verificar se coluna departamento existe
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.columns 
                WHERE table_schema = 'inventario' 
                AND table_name = 'user_table' 
                AND column_name = 'departamento'
            """)
            if cursor.fetchone()[0] == 0:
                print("Adicionando coluna 'departamento'...")
                cursor.execute("""
                    ALTER TABLE user_table 
                    ADD COLUMN departamento VARCHAR(60) NULL AFTER nome_completo
                """)
                print("✅ Coluna 'departamento' adicionada!")
            else:
                print("ℹ️ Coluna 'departamento' já existe.")
        
        connection.commit()
        print("\n✅ Migração concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        raise
    finally:
        if 'connection' in dir() and connection:
            connection.close()

if __name__ == "__main__":
    add_user_fields()
