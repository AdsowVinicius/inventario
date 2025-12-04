from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re
import html


def sanitize_string(value: str, max_length: int = 500) -> str:
    """Sanitiza string removendo caracteres perigosos"""
    if not value:
        return value
    # Escapar HTML
    value = html.escape(str(value).strip())
    # Remover caracteres de controle
    value = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', value)
    # Limitar tamanho
    return value[:max_length]


def check_sql_injection(value: str) -> bool:
    """Detecta padrões de SQL Injection"""
    if not value:
        return False
    patterns = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|TRUNCATE|ALTER|CREATE|EXEC)\b)",
        r"(--|\#|\/\*|\*\/)",
        r"(\bOR\b\s+\d+\s*=\s*\d+)",
        r"(\bUNION\b.*\bSELECT\b)",
        r"(';|\"--|;--)",
    ]
    value_upper = value.upper()
    for pattern in patterns:
        if re.search(pattern, value_upper, re.IGNORECASE):
            return True
    return False


class ContagemBase(BaseModel):
    """Schema base de contagem com validações de segurança"""
    planta: str = Field(..., min_length=2, max_length=10)
    zona_inventario: str = Field(..., min_length=1, max_length=5)
    etiqueta_inventario: str = Field(..., min_length=1, max_length=10)
    part_number: str = Field(..., min_length=1, max_length=50)
    campo: Optional[str] = Field(None, max_length=100)
    qtd: float = Field(..., ge=0, le=99999999)
    
    @field_validator('planta')
    @classmethod
    def validate_planta(cls, v):
        if not v:
            raise ValueError('Planta é obrigatória')
        v = sanitize_string(v, 10)
        plantas_validas = {'PS01', 'PS02', 'PS03', 'PS05', 'PB82'}
        if v.upper() not in plantas_validas:
            raise ValueError(f'Planta inválida. Valores permitidos: {plantas_validas}')
        if check_sql_injection(v):
            raise ValueError('Caracteres inválidos detectados')
        return v.upper()
    
    @field_validator('zona_inventario')
    @classmethod
    def validate_zona(cls, v):
        if not v:
            raise ValueError('Zona é obrigatória')
        v = sanitize_string(v, 5)
        if not re.match(r'^[A-Za-z0-9]{1,5}$', v):
            raise ValueError('Zona deve conter apenas letras e números')
        if check_sql_injection(v):
            raise ValueError('Caracteres inválidos detectados')
        return v.upper()
    
    @field_validator('etiqueta_inventario')
    @classmethod
    def validate_etiqueta(cls, v):
        if not v:
            raise ValueError('Etiqueta é obrigatória')
        v = sanitize_string(v, 10)
        # Permitir números, podendo ter zeros à esquerda removidos
        if not re.match(r'^\d{1,10}$', v):
            raise ValueError('Etiqueta deve conter apenas números (máx 10 dígitos)')
        if check_sql_injection(v):
            raise ValueError('Caracteres inválidos detectados')
        return v
    
    @field_validator('part_number')
    @classmethod
    def validate_part_number(cls, v):
        if not v:
            raise ValueError('Part Number é obrigatório')
        v = sanitize_string(v, 50)
        # Permitir alfanuméricos, hífen, ponto, underscore
        if not re.match(r'^[A-Za-z0-9\-_.]{1,50}$', v):
            raise ValueError('Part Number contém caracteres inválidos')
        if check_sql_injection(v):
            raise ValueError('Caracteres inválidos detectados')
        return v
    
    @field_validator('campo')
    @classmethod
    def validate_campo(cls, v):
        if v is None:
            return v
        v = sanitize_string(v, 100)
        if check_sql_injection(v):
            raise ValueError('Caracteres inválidos detectados')
        return v


class ContagemCreate(ContagemBase):
    """Schema para criar contagem - num_contagem pode ser informado manualmente"""
    num_contagem: Optional[int] = Field(None, ge=1, le=3)


class ContagemUpdate(BaseModel):
    """Schema para atualizar contagem"""
    zona_inventario: Optional[str] = Field(None, max_length=5)
    etiqueta_inventario: Optional[str] = Field(None, max_length=10)
    part_number: Optional[str] = Field(None, max_length=50)
    campo: Optional[str] = Field(None, max_length=100)
    qtd: Optional[float] = Field(None, ge=0, le=99999999)
    num_contagem: Optional[int] = Field(None, ge=1, le=3)
    
    @field_validator('zona_inventario', 'etiqueta_inventario', 'part_number', 'campo')
    @classmethod
    def validate_strings(cls, v):
        if v is None:
            return v
        v = sanitize_string(v, 100)
        if check_sql_injection(v):
            raise ValueError('Caracteres inválidos detectados')
        return v


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
    """Schema para filtros de exportação com validação"""
    planta: Optional[str] = Field(None, max_length=10)
    zona_inventario: Optional[str] = Field(None, max_length=5)
    etiqueta_inventario: Optional[str] = Field(None, max_length=10)
    part_number: Optional[str] = Field(None, max_length=50)
    num_contagem: Optional[int] = Field(None, ge=1, le=3)
    
    @field_validator('planta', 'zona_inventario', 'etiqueta_inventario', 'part_number')
    @classmethod
    def validate_filter_strings(cls, v):
        if v is None:
            return v
        v = sanitize_string(v, 50)
        if check_sql_injection(v):
            raise ValueError('Caracteres inválidos detectados no filtro')
        return v


class MessageResponse(BaseModel):
    """Schema para resposta de mensagem"""
    status: str
    mensagem: str

