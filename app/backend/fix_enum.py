#!/usr/bin/env python
"""
Script para corrigir o enum de roles alterando diretamente a estrutura da tabela
"""
import sys
from sqlalchemy import create_engine, text

# URL do banco sem senha
DATABASE_URL = "mysql+pymysql://root@localhost:3306/inventario"

print("🔧 Corrigindo enum de roles...")

try:
    # Criar engine
    engine = create_engine(DATABASE_URL, echo=True)
    
    # Conectar e executar SQL bruto
    with engine.connect() as conn:
        # Alterar a definição do enum na tabela
        print("\n📝 Alterando definição do enum...")
        conn.execute(text("""
            ALTER TABLE user_table 
            MODIFY COLUMN role ENUM('ADMIN', 'ENCARREGADO', 'CONTADOR') 
            NOT NULL DEFAULT 'CONTADOR'
        """))
        conn.commit()
        
        print("\n✅ Enum alterado com sucesso!")
        
        # Verificar usuários
        print("\n👥 Usuários na tabela:")
        result = conn.execute(text("SELECT id, user_name, role, planta FROM user_table"))
        for row in result:
            print(f"  - {row.user_name}: {row.role} ({row.planta})")
            
except Exception as e:
    print(f"\n❌ Erro: {e}")
    sys.exit(1)

print("\n✅ Correção concluída!")
