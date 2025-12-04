from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ContagemBase(BaseModel):
    """Schema base de contagem"""
    planta: str
    zona_inventario: str
    etiqueta_inventario: str
    part_number: str
    campo: Optional[str] = None
    qtd: float = Field(..., ge=0)


class ContagemCreate(ContagemBase):
    """Schema para criar contagem - num_contagem pode ser informado manualmente"""
    num_contagem: Optional[int] = Field(None, ge=1)


class ContagemUpdate(BaseModel):
    """Schema para atualizar contagem"""
    zona_inventario: Optional[str] = None
    etiqueta_inventario: Optional[str] = None
    part_number: Optional[str] = None
    campo: Optional[str] = None
    qtd: Optional[float] = Field(None, ge=0)
    num_contagem: Optional[int] = Field(None, ge=1, le=3)


class ContagemResponse(ContagemBase):
    """Schema de resposta de contagem"""
    id: int
    num_contagem: int
    usuario_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


class ContagemListResponse(BaseModel):
    """Schema de resposta de contagem com nome do usuário"""
    id: int
    planta: str
    zona_inventario: str
    etiqueta_inventario: str
    part_number: str
    campo: Optional[str] = None
    qtd: float
    num_contagem: int
    usuario_id: int
    usuario_nome: str
    timestamp: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ContagemSugestaoResponse(BaseModel):
    """Schema para sugestão de número de contagem"""
    num_contagem_sugerido: int
    total_contagens: int
    limite_atingido: bool = False


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
