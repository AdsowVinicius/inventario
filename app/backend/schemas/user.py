from pydantic import BaseModel, Field
from typing import Optional
from models.user import PlantaEnum, RoleEnum


class UserBase(BaseModel):
    """Schema base de usuário"""
    user_name: str = Field(..., min_length=3, max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    planta: PlantaEnum
    role: RoleEnum = RoleEnum.CONTADOR


class UserCreate(UserBase):
    """Schema para criar usuário"""
    senha: str = Field(..., min_length=6)


class UserResponse(UserBase):
    """Schema de resposta de usuário"""
    id: int
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema para atualizar usuário"""
    user_name: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    senha: Optional[str] = Field(None, min_length=6)
    planta: Optional[PlantaEnum] = None
    role: Optional[RoleEnum] = None


class UserLogin(BaseModel):
    """Schema para login"""
    user_name: str
    senha: str


class TokenResponse(BaseModel):
    """Schema de resposta do token"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
