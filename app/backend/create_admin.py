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
        password = "admin123"

        # Verificar comprimento em bytes e avisar (hash_password trunca se necessário)
        try:
            pwb = password.encode("utf-8")
        except Exception:
            pwb = None

        if pwb is not None and len(pwb) > 72:
            print("⚠️ Senha excede 72 bytes e será truncada ao gerar o hash.")

        admin = User(
            user_name="admin",
            senha_hash=hash_password(password),
            planta=PlantaEnum.PS01,
            role=RoleEnum.ADMIN
        )

        db.add(admin)
        db.commit()

        print("✅ Usuário admin criado com sucesso!")
        print("   Usuário: admin")
        print(f"   Senha: {password}")
        print("   ⚠️  IMPORTANTE: Altere a senha após o primeiro login!")

except Exception as e:
    print(f"❌ Erro ao criar usuário: {e}")
    db.rollback()

finally:
    db.close()
