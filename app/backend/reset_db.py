"""
Script para recriar tabelas (DROP e CREATE)
ATENÇÃO: Isso vai apagar todos os dados!
"""

from core.database import Base, engine
from core.security import hash_password
from models import User, PlantaEnum, RoleEnum, ItensInventario, FormsContagem
from sqlalchemy.orm import sessionmaker

print("⚠️ ATENÇÃO: Este script vai APAGAR todos os dados!")
print("")

# Dropar todas as tabelas
print("🗑️ Dropando tabelas antigas...")
Base.metadata.drop_all(bind=engine)
print("✅ Tabelas antigas removidas!")

# Criar todas as tabelas
print("🏗️ Criando novas tabelas...")
Base.metadata.create_all(bind=engine)
print("✅ Tabelas criadas com sucesso!")

# Criar usuário admin
print("👤 Criando usuário admin...")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    admin = User(
        user_name="admin",
        senha_hash=hash_password("admin123"),
        planta=PlantaEnum.PS01,
        role=RoleEnum.ADMIN
    )
    
    db.add(admin)
    db.commit()
    
    print("✅ Usuário admin criado!")
    print("   Usuário: admin")
    print("   Senha: admin123")
    print("   Planta: PS01")
    print("   Role: ADMIN")
    
except Exception as e:
    print(f"❌ Erro ao criar admin: {e}")
    db.rollback()
    
finally:
    db.close()

print("")
print("✅ Setup completo! Banco de dados pronto para uso!")
