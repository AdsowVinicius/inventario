"""
Script para criar tabelas e usuário admin
"""

from core.database import SessionLocal, init_db
from core.security import hash_password
from models.user import User, PlantaEnum, RoleEnum

print("🗄️ Criando tabelas no banco de dados...")
init_db()
print("✅ Tabelas criadas!")

db = SessionLocal()

try:
    # Verificar se já existe admin
    existing_admin = db.query(User).filter(User.user_name == "admin").first()
    
    if existing_admin:
        print("⚠️ Usuário 'admin' já existe!")
        print(f"   Planta: {existing_admin.planta}")
        print(f"   Role: {existing_admin.role}")
    else:
        # Criar usuário admin
        admin = User(
            user_name="admin",
            senha_hash=hash_password("admin123"),
            planta=PlantaEnum.PS01,
            role=RoleEnum.ADMIN
        )
        
        db.add(admin)
        db.commit()
        
        print("✅ Usuário admin criado com sucesso!")
        print("   Usuário: admin")
        print("   Senha: admin123")
        print("   Planta: PS01")
        print("   Role: ADMIN")
        print("")
        print("⚠️ IMPORTANTE: Altere a senha após o primeiro login!")

except Exception as e:
    print(f"❌ Erro: {e}")
    db.rollback()

finally:
    db.close()

print("")
print("✅ Setup concluído!")
