"""
Script para adicionar coluna updated_at na tabela forms_contagem
"""

from sqlalchemy import create_engine, text
from core.config import settings

def add_updated_at_column():
    """Adiciona coluna updated_at se não existir"""
    engine = create_engine(settings.DATABASE_URL)

    dialect = engine.dialect.name.lower()

    with engine.connect() as conn:
        try:
            # Verificar existência da tabela/coluna de forma compatível com o dialeto
            if dialect in ("mysql", "mariadb"):
                result = conn.execute(text("""
                    SELECT COUNT(*) as count
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                      AND TABLE_NAME = 'forms_contagem'
                      AND COLUMN_NAME = 'updated_at'
                """))
                exists = result.scalar() or 0

                if exists == 0:
                    print("📝 Adicionando coluna updated_at (MySQL)...")
                    conn.execute(text("""
                        ALTER TABLE forms_contagem
                        ADD COLUMN updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    """))
                    # Inicializar: se houver coluna 'timestamp' use ela, caso contrário use NOW()
                    col_check = conn.execute(text("""
                        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'forms_contagem' AND COLUMN_NAME = 'timestamp'
                    """))
                    has_ts = (col_check.scalar() or 0) > 0
                    if has_ts:
                        conn.execute(text("""UPDATE forms_contagem SET updated_at = `timestamp`"""))
                    else:
                        conn.execute(text("""UPDATE forms_contagem SET updated_at = NOW()"""))
                    conn.commit()
                    print("✅ Coluna updated_at adicionada com sucesso!")
                else:
                    print("ℹ️ Coluna updated_at já existe (MySQL)")

            elif dialect == "sqlite":
                # SQLite: usar PRAGMA para checar colunas
                result = conn.execute(text("PRAGMA table_info('forms_contagem')"))
                cols = [row[1] for row in result.fetchall()]
                if 'updated_at' in cols:
                    print("ℹ️ Coluna updated_at já existe (SQLite)")
                else:
                    print("📝 Adicionando coluna updated_at (SQLite)...")
                    # SQLite não permite adicionar coluna com default não-constante em ALTER TABLE
                    # Adicionamos coluna nullable e inicializamos os valores em seguida
                    conn.execute(text("ALTER TABLE forms_contagem ADD COLUMN updated_at DATETIME"))
                    # Inicializar valores: use coluna 'timestamp' se existir, senão CURRENT_TIMESTAMP
                    if 'timestamp' in cols:
                        conn.execute(text("UPDATE forms_contagem SET updated_at = timestamp"))
                    else:
                        conn.execute(text("UPDATE forms_contagem SET updated_at = CURRENT_TIMESTAMP"))
                    conn.commit()
                    print("✅ Coluna updated_at adicionada com sucesso! (SQLite)")

            else:
                # Dialeto desconhecido: tentar abordagem genérica
                print(f"⚠️ Dialeto desconhecido '{dialect}', tentando método genérico...")
                # Tentar INFORMATION_SCHEMA, se falhar, informar ao usuário
                result = conn.execute(text("""
                    SELECT COUNT(*) as count
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = 'forms_contagem' AND COLUMN_NAME = 'updated_at'
                """))
                exists = result.scalar() or 0
                if exists == 0:
                    print("📝 Adicionando coluna updated_at (genérico)...")
                    conn.execute(text("ALTER TABLE forms_contagem ADD COLUMN updated_at DATETIME"))
                    conn.commit()
                    print("✅ Coluna added (genérico) — verifique manualmente propriedades de DEFAULT/ON UPDATE")
                else:
                    print("ℹ️ Coluna updated_at já existe (genérico)")

        except Exception as e:
            print(f"❌ Erro: {e}")
            conn.rollback()

if __name__ == "__main__":
    add_updated_at_column()
