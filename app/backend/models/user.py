from sqlalchemy import Column, Integer, String, Enum
from core.database import Base
import enum


class PlantaEnum(str, enum.Enum):
    """Enum para plantas"""
    PS01 = "PS01"
    PS02 = "PS02"
    PS03 = "PS03"
    PS05 = "PS05"
    PS09 = "PS09"
    PB82 = "PB82"


class RoleEnum(str, enum.Enum):
    """Enum para papéis de usuário"""
    ADMIN = "ADMIN"
    ENCARREGADO = "ENCARREGADO"
    CONTADOR = "CONTADOR"


class User(Base):
    """Model de usuário"""
    __tablename__ = "user_table"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_name = Column(String(100), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    planta = Column(Enum(PlantaEnum), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.CONTADOR)
    
    def __repr__(self):
        return f"<User(id={self.id}, user_name={self.user_name}, planta={self.planta}, role={self.role})>"
