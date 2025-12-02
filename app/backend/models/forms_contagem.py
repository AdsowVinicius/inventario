from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base


class FormsContagem(Base):
    """Model de contagem (sem lote)"""
    __tablename__ = "forms_contagem"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    planta = Column(String(10), nullable=False, index=True)
    num_contagem = Column(Integer, nullable=False, index=True)
    zona_inventario = Column(String(50), nullable=False, index=True)
    etiqueta_inventario = Column(String(50), nullable=False, index=True)
    part_number = Column(String(50), nullable=False, index=True)
    campo = Column(String(100), nullable=True)
    qtd = Column(Float, nullable=False, default=0.0)
    usuario_id = Column(Integer, ForeignKey("user_table.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamento com usuário
    usuario = relationship("User", foreign_keys=[usuario_id])
    
    def __repr__(self):
        return f"<FormsContagem(id={self.id}, planta={self.planta}, num_contagem={self.num_contagem}, part_number={self.part_number})>"
