"""
Script para adicionar coluna primeiro_login na tabela user_table
"""
from sqlalchemy import create_engine, text
from core.config import settings

def add_primeiro_login_column():
    """Adiciona a coluna primeiro_login se não existir"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Verificar se a coluna já existe
        result = conn.execute(text("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'inventario' 
            AND TABLE_NAME = 'user_table' 
            AND COLUMN_NAME = 'primeiro_login'
        """))
        
        if result.fetchone() is None:
            # Adicionar coluna primeiro_login (padrão True para novos usuários)
            conn.execute(text("""
                ALTER TABLE user_table 
                ADD COLUMN primeiro_login BOOLEAN NOT NULL DEFAULT FALSE
            """))
            conn.commit()
            print("✓ Coluna 'primeiro_login' adicionada com sucesso!")
            
            # Atualizar usuários existentes para primeiro_login = FALSE
            # (usuários já existentes não precisam trocar a senha)
            conn.execute(text("""
                UPDATE user_table SET primeiro_login = FALSE WHERE primeiro_login IS NULL
            """))
            conn.commit()
            print("✓ Usuários existentes atualizados para primeiro_login = FALSE")
        else:
            print("✓ Coluna 'primeiro_login' já existe")

if __name__ == "__main__":
    add_primeiro_login_column()
