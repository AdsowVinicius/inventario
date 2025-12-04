from pydantic import BaseModel
from typing import Optional


class ItensInventarioBase(BaseModel):
    """Schema base de item de inventário"""
    num_material: str
    txt_descrica_material: Optional[str] = None
    planta: str
    deposito: Optional[str] = None
    tipo_material: Optional[str] = None
    und_medida: Optional[str] = None


class ItensInventarioCreate(ItensInventarioBase):
    """Schema para criar item de inventário"""
    pass


class ItensInventarioUpdate(BaseModel):
    """Schema para atualizar item de inventário"""
    num_material: Optional[str] = None
    txt_descrica_material: Optional[str] = None
    planta: Optional[str] = None
    deposito: Optional[str] = None
    tipo_material: Optional[str] = None
    und_medida: Optional[str] = None


class ItensInventarioResponse(ItensInventarioBase):
    """Schema de resposta de item de inventário"""
    id: int
    
    class Config:
        from_attributes = True


class PartNumberResponse(BaseModel):
    """Schema para lista de part numbers"""
    part_number: str
    descricao: Optional[str] = None
    und_medida: Optional[str] = None
