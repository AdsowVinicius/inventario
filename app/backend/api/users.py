"""
API de Gestão de Usuários
- ADMIN: Pode gerenciar todos os usuários
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from models.user import User, RoleEnum, PlantaEnum
from schemas.user import UserCreate, UserResponse, UserUpdate
from core.security import get_current_user, hash_password, require_role

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserResponse])
async def listar_usuarios(
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """
    Listar usuários - Apenas ADMIN
    """
    usuarios = db.query(User).all()
    return usuarios


@router.get("/{user_id}", response_model=UserResponse)
async def obter_usuario(
    user_id: int,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """
    Obter usuário por ID - Apenas ADMIN
    """
    usuario = db.query(User).filter(User.id == user_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return usuario


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def criar_usuario(
    user_data: UserCreate,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """
    Criar novo usuário - Apenas ADMIN
    """
    # Verificar se username já existe
    usuario_existente = db.query(User).filter(User.user_name == user_data.user_name).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome de usuário já existe"
        )
    
    # Criar novo usuário
    novo_usuario = User(
        user_name=user_data.user_name,
        email=user_data.email,
        nome_completo=user_data.nome_completo,
        departamento=user_data.departamento,
        senha_hash=hash_password(user_data.senha),
        planta=user_data.planta,
        role=user_data.role
    )
    
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    
    return novo_usuario


@router.put("/{user_id}", response_model=UserResponse)
async def atualizar_usuario(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """
    Atualizar usuário - Apenas ADMIN
    """
    usuario = db.query(User).filter(User.id == user_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Atualizar campos
    if user_data.user_name:
        # Verificar se novo username já existe
        if user_data.user_name != usuario.user_name:
            existente = db.query(User).filter(User.user_name == user_data.user_name).first()
            if existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Nome de usuário já existe"
                )
        usuario.user_name = user_data.user_name
    
    if user_data.email is not None:
        usuario.email = user_data.email
    
    if user_data.nome_completo is not None:
        usuario.nome_completo = user_data.nome_completo
    
    if user_data.departamento is not None:
        usuario.departamento = user_data.departamento

    if user_data.senha:
        usuario.senha_hash = hash_password(user_data.senha)
    
    if user_data.planta:
        usuario.planta = user_data.planta
    
    if user_data.role:
        usuario.role = user_data.role
    
    db.commit()
    db.refresh(usuario)
    
    return usuario


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_usuario(
    user_id: int,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """
    Deletar usuário - Apenas ADMIN
    """
    usuario = db.query(User).filter(User.id == user_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Não pode deletar a si mesmo
    if usuario.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você não pode deletar sua própria conta"
        )
    
    db.delete(usuario)
    db.commit()
    
    return None
