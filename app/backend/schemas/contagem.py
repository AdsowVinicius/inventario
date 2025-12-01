from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ContagemBase(BaseModel):
    """Schema base de contagem"""
    planta: str
    num_contagem: int = Field(..., ge=1)
    zona_inventario: str
    etiqueta_inventario: str
    part_number: str
    campo: Optional[str] = None
    qtd: float = Field(..., ge=0)


class ContagemCreate(ContagemBase):
    """Schema para criar contagem"""
    pass


class ContagemResponse(ContagemBase):
    """Schema de resposta de contagem"""
    id: int
    usuario_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


class ContagemSugestaoResponse(BaseModel):
    """Schema para sugestão de número de contagem"""
    num_contagem_sugerido: int
    total_contagens: int


class ContagemFiltros(BaseModel):
    """Schema para filtros de exportação"""
    planta: Optional[str] = None
    zona_inventario: Optional[str] = None
    etiqueta_inventario: Optional[str] = None
    part_number: Optional[str] = None
    num_contagem: Optional[int] = None


class MessageResponse(BaseModel):
    """Schema para resposta de mensagem"""
    status: str
    mensagem: str
