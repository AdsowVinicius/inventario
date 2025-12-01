from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import hash_password, verify_password, create_access_token
from models.user import User
from schemas.user import UserLogin, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Endpoint de login
    
    Verifica credenciais e retorna token JWT
    """
    # Buscar usuário
    user = db.query(User).filter(User.user_name == credentials.user_name).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos"
        )
    
    # Verificar senha
    if not verify_password(credentials.senha, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos"
        )
    
    # Criar token JWT
    token_data = {
        "id": user.id,
        "user_name": user.user_name,
        "planta": user.planta.value,
        "role": user.role.value
    }
    
    access_token = create_access_token(token_data)
    
    # Retornar token e dados do usuário
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            user_name=user.user_name,
            planta=user.planta,
            role=user.role
        )
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(lambda: __import__('core.security', fromlist=['get_current_user']).get_current_user)):
    """
    Retorna informações do usuário autenticado
    """
    return UserResponse(
        id=current_user.id,
        user_name=current_user.user_name,
        planta=current_user.planta,
        role=current_user.role
    )
