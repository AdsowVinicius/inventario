from pydantic import BaseModel, Field, field_validator
from typing import Optional
from models.user import PlantaEnum, RoleEnum
import re
import html


def sanitize_string(value: str, max_length: int = 255) -> str:
    """Sanitiza string removendo caracteres perigosos"""
    if not value:
        return value
    value = html.escape(str(value).strip())
    value = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', value)
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


class UserBase(BaseModel):
    """Schema base de usuário com validações de segurança"""
    user_name: str = Field(..., min_length=3, max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    nome_completo: Optional[str] = Field(None, max_length=60)
    departamento: Optional[str] = Field(None, max_length=60)
    planta: PlantaEnum
    role: RoleEnum = RoleEnum.CONTADOR
    
    @field_validator('user_name')
    @classmethod
    def validate_user_name(cls, v):
        if not v:
            raise ValueError('Nome de usuário é obrigatório')
        v = sanitize_string(v, 100)
        # Permitir apenas alfanuméricos, underscore e ponto
        if not re.match(r'^[A-Za-z0-9_.]{3,100}$', v):
            raise ValueError('Nome de usuário deve conter apenas letras, números, _ e .')
        if check_sql_injection(v):
            raise ValueError('Caracteres inválidos detectados')
        return v.lower()
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if v is None or v == '':
            return None  # Converter string vazia para None
        v = sanitize_string(v, 255)
        # Validação básica de email
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Email inválido')
        if check_sql_injection(v):
            raise ValueError('Caracteres inválidos detectados')
        return v.lower()
    
    @field_validator('nome_completo', 'departamento')
    @classmethod
    def validate_text_fields(cls, v):
        if v is None:
            return v
        v = sanitize_string(v, 60)
        if check_sql_injection(v):
            raise ValueError('Caracteres inválidos detectados')
        return v


class UserCreate(UserBase):
    """Schema para criar usuário"""
    senha: str = Field(..., min_length=6, max_length=128)
    
    @field_validator('senha')
    @classmethod
    def validate_senha(cls, v):
        if not v or len(v) < 6:
            raise ValueError('Senha deve ter no mínimo 6 caracteres')
        # Verificar complexidade básica
        if len(v) > 128:
            raise ValueError('Senha muito longa')
        return v


class UserResponse(UserBase):
    """Schema de resposta de usuário"""
    id: int
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema para atualizar usuário"""
    user_name: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    nome_completo: Optional[str] = Field(None, max_length=60)
    departamento: Optional[str] = Field(None, max_length=60)
    senha: Optional[str] = Field(None, min_length=6, max_length=128)
    planta: Optional[PlantaEnum] = None
    role: Optional[RoleEnum] = None
    
    @field_validator('user_name', 'email', 'nome_completo', 'departamento')
    @classmethod
    def validate_update_strings(cls, v):
        if v is None:
            return v
        v = sanitize_string(v, 255)
        if check_sql_injection(v):
            raise ValueError('Caracteres inválidos detectados')
        return v


class UserLogin(BaseModel):
    """Schema para login com proteções"""
    user_name: str = Field(..., min_length=1, max_length=100)
    senha: str = Field(..., min_length=1, max_length=128)
    
    @field_validator('user_name')
    @classmethod
    def validate_login_username(cls, v):
        if not v:
            raise ValueError('Nome de usuário é obrigatório')
        v = sanitize_string(v, 100)
        if check_sql_injection(v):
            raise ValueError('Caracteres inválidos')
        return v
    
    @field_validator('senha')
    @classmethod
    def validate_login_senha(cls, v):
        if not v:
            raise ValueError('Senha é obrigatória')
        # Não sanitizar senha, mas verificar tamanho
        if len(v) > 128:
            raise ValueError('Senha inválida')
        return v


class TokenResponse(BaseModel):
    """Schema de resposta do token"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

