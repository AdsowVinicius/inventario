"""
Script para criar usuário admin inicial
Execute após configurar o banco de dados
"""

from core.database import SessionLocal, init_db
from core.security import hash_password
from models.user import User, PlantaEnum, RoleEnum

# Inicializar banco
print("Criando tabelas no banco de dados...")
init_db()

# Criar sessão
db = SessionLocal()

try:
    # Verificar se já existe admin
    existing_admin = db.query(User).filter(User.user_name == "admin").first()
    
    if existing_admin:
        print("❌ Usuário 'admin' já existe!")
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
        print("   ⚠️  IMPORTANTE: Altere a senha após o primeiro login!")

except Exception as e:
    print(f"❌ Erro ao criar usuário: {e}")
    db.rollback()

finally:
    db.close()
