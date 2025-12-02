#!/usr/bin/env python3
"""
Script para adicionar coluna email na tabela user_table
"""

import pymysql

def add_email_column():
    """Adiciona coluna email à tabela user_table"""
    
    connection = None
    try:
        # Conectar ao banco
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='inventario',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # Verificar se a coluna já existe
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = 'inventario'
                AND TABLE_NAME = 'user_table'
                AND COLUMN_NAME = 'email'
            """)
            
            result = cursor.fetchone()
            
            if result['count'] > 0:
                print("✅ Coluna 'email' já existe na tabela user_table")
                return
            
            # Adicionar coluna email
            print("📝 Adicionando coluna email...")
            cursor.execute("""
                ALTER TABLE user_table
                ADD COLUMN email VARCHAR(255) NULL AFTER user_name
            """)
            
            # Atualizar emails existentes com base no user_name
            print("📧 Atualizando emails dos usuários existentes...")
            cursor.execute("""
                UPDATE user_table
                SET email = CONCAT(user_name, '@inventario.com')
                WHERE email IS NULL
            """)
            
            connection.commit()
            print("✅ Coluna email adicionada e emails atualizados com sucesso!")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        raise
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    add_email_column()
