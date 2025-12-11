from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import pytz
from core.database import Base

# Fuso horário de Brasília
BRAZIL_TZ = pytz.timezone('America/Sao_Paulo')

def get_brazil_now():
    """Retorna a data/hora atual no fuso de Brasília"""
    return datetime.now(BRAZIL_TZ).replace(tzinfo=None)


class FormsContagem(Base):
    """Model de contagem de inventário"""
    __tablename__ = "forms_contagem"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    planta = Column(String(10), nullable=False, index=True)
    num_contagem = Column(Integer, nullable=False, index=True)
    zona_inventario = Column(String(50), nullable=False, index=True)
    etiqueta_inventario = Column(String(50), nullable=False, index=True)
    part_number = Column(String(50), nullable=False, index=True)
    lote = Column(String(100), nullable=True)
    qtd = Column(Float, nullable=False, default=0.0)
    usuario_id = Column(Integer, ForeignKey("user_table.id"), nullable=False)
    timestamp = Column(DateTime, default=get_brazil_now, nullable=False)
    updated_at = Column(DateTime, default=get_brazil_now, onupdate=get_brazil_now, nullable=False)
    
    # Relacionamento com usuário
    usuario = relationship("User", foreign_keys=[usuario_id])
    
    def __repr__(self):
        return f"<FormsContagem(id={self.id}, planta={self.planta}, num_contagem={self.num_contagem}, part_number={self.part_number})>"
