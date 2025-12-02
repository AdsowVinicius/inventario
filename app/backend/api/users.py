"""
API de Gestão de Usuários
- ADMIN: Pode gerenciar usuários de todas as plantas
- ENCARREGADO: Pode gerenciar apenas usuários de sua própria planta
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
    current_user: User = Depends(require_role("ADMIN", "ENCARREGADO")),
    db: Session = Depends(get_db)
):
    """
    Listar usuários
    - ADMIN: Vê todos os usuários de todas as plantas
    - ENCARREGADO: Vê apenas usuários de sua planta
    """
    if current_user.role == "ADMIN":
        # Admin vê todos
        usuarios = db.query(User).all()
    else:
        # Encarregado vê apenas sua planta
        usuarios = db.query(User).filter(User.planta == current_user.planta).all()
    
    return usuarios


@router.get("/{user_id}", response_model=UserResponse)
async def obter_usuario(
    user_id: int,
    current_user: User = Depends(require_role("ADMIN", "ENCARREGADO")),
    db: Session = Depends(get_db)
):
    """
    Obter usuário por ID
    - ADMIN: Pode ver qualquer usuário
    - ENCARREGADO: Só pode ver usuários de sua planta
    """
    usuario = db.query(User).filter(User.id == user_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Verificar permissão
    if current_user.role == "ENCARREGADO" and usuario.planta != current_user.planta:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode visualizar usuários de sua planta"
        )
    
    return usuario


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def criar_usuario(
    user_data: UserCreate,
    current_user: User = Depends(require_role("ADMIN", "ENCARREGADO")),
    db: Session = Depends(get_db)
):
    """
    Criar novo usuário
    - ADMIN: Pode criar usuários em qualquer planta
    - ENCARREGADO: Só pode criar usuários em sua própria planta
    """
    # Verificar se username já existe
    usuario_existente = db.query(User).filter(User.user_name == user_data.user_name).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome de usuário já existe"
        )
    
    # ENCARREGADO só pode criar na sua planta
    if current_user.role == "ENCARREGADO":
        if user_data.planta != current_user.planta:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você só pode criar usuários em sua própria planta"
            )
        
        # ENCARREGADO não pode criar ADMIN
        if user_data.role == "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para criar usuários ADMIN"
            )
    
    # Criar novo usuário
    novo_usuario = User(
        user_name=user_data.user_name,
        email=user_data.email,
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
    current_user: User = Depends(require_role("ADMIN", "ENCARREGADO")),
    db: Session = Depends(get_db)
):
    """
    Atualizar usuário
    - ADMIN: Pode atualizar qualquer usuário
    - ENCARREGADO: Só pode atualizar usuários de sua planta (exceto ADMIN)
    """
    usuario = db.query(User).filter(User.id == user_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Verificar permissões
    if current_user.role == "ENCARREGADO":
        # Não pode editar usuários de outra planta
        if usuario.planta != current_user.planta:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você só pode editar usuários de sua planta"
            )
        
        # Não pode editar ADMIN
        if usuario.role == "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não pode editar usuários ADMIN"
            )
        
        # Não pode mudar role para ADMIN
        if user_data.role == "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não pode promover usuários a ADMIN"
            )
        
        # Não pode mudar planta
        if user_data.planta and user_data.planta != current_user.planta:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não pode mudar usuários para outra planta"
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
    current_user: User = Depends(require_role("ADMIN", "ENCARREGADO")),
    db: Session = Depends(get_db)
):
    """
    Deletar usuário
    - ADMIN: Pode deletar qualquer usuário (exceto ele mesmo)
    - ENCARREGADO: Só pode deletar usuários de sua planta (exceto ADMIN)
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
    
    # Verificar permissões
    if current_user.role == "ENCARREGADO":
        # Não pode deletar usuários de outra planta
        if usuario.planta != current_user.planta:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você só pode deletar usuários de sua planta"
            )
        
        # Não pode deletar ADMIN
        if usuario.role == "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não pode deletar usuários ADMIN"
            )
    
    db.delete(usuario)
    db.commit()
    
    return None
