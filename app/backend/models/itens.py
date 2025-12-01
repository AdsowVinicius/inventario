from sqlalchemy import Column, Integer, String
from core.database import Base


class ItensInventario(Base):
    """Model de itens do inventário"""
    __tablename__ = "itens_inventario"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    num_material = Column(String(50), nullable=False, index=True)
    txt_descrica_material = Column(String(255), nullable=True)
    planta = Column(String(10), nullable=False, index=True)
    deposito = Column(String(50), nullable=True)
    tipo_material = Column(String(50), nullable=True)
    und_medida = Column(String(10), nullable=True)
    
    def __repr__(self):
        return f"<ItensInventario(id={self.id}, num_material={self.num_material}, planta={self.planta})>"
