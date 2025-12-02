"""
Script para adicionar coluna updated_at na tabela forms_contagem
"""

from sqlalchemy import create_engine, text
from core.config import settings

def add_updated_at_column():
    """Adiciona coluna updated_at se não existir"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # Verificar se a coluna já existe
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'forms_contagem' 
                AND COLUMN_NAME = 'updated_at'
            """))
            
            exists = result.fetchone()[0]
            
            if exists == 0:
                print("📝 Adicionando coluna updated_at...")
                
                # Adicionar coluna
                conn.execute(text("""
                    ALTER TABLE forms_contagem 
                    ADD COLUMN updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                """))
                
                # Inicializar com o valor de timestamp
                conn.execute(text("""
                    UPDATE forms_contagem 
                    SET updated_at = timestamp
                """))
                
                conn.commit()
                print("✅ Coluna updated_at adicionada com sucesso!")
            else:
                print("ℹ️ Coluna updated_at já existe")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            conn.rollback()

if __name__ == "__main__":
    add_updated_at_column()
