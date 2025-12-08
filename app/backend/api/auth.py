from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import hash_password, verify_password, create_access_token, get_current_user
from core.security_utils import (
    rate_limiter, 
    log_security_event, 
    sanitize_string,
    check_input_safety
)
from models.user import User
from schemas.user import UserLogin, TokenResponse, UserResponse
import logging

router = APIRouter(prefix="/auth", tags=["Autenticação"])
logger = logging.getLogger(__name__)

# Controle de tentativas de login falhas
_failed_attempts: dict = {}


def get_client_ip(request: Request) -> str:
    """Obtém IP do cliente considerando proxy"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def check_brute_force(ip: str, username: str) -> bool:
    """
    Verifica se há tentativa de brute force.
    Bloqueia após 5 tentativas falhas em 5 minutos.
    """
    key = f"{ip}:{username}"
    attempts = _failed_attempts.get(key, 0)
    return attempts >= 5


def record_failed_attempt(ip: str, username: str):
    """Registra tentativa de login falha"""
    key = f"{ip}:{username}"
    _failed_attempts[key] = _failed_attempts.get(key, 0) + 1


def clear_failed_attempts(ip: str, username: str):
    """Limpa tentativas falhas após login bem sucedido"""
    key = f"{ip}:{username}"
    if key in _failed_attempts:
        del _failed_attempts[key]


@router.post("/login", response_model=TokenResponse)
def login(
    credentials: UserLogin, 
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Endpoint de login com proteções contra brute force
    
    Verifica credenciais e retorna token JWT
    """
    client_ip = get_client_ip(request)
    
    # Verificar rate limit específico para login
    login_key = f"login:{client_ip}"
    if not rate_limiter.is_allowed(login_key, max_requests=10, window_seconds=60):
        log_security_event(
            "LOGIN_RATE_LIMITED",
            "Too many login attempts",
            ip_address=client_ip,
            extra_data={"username": credentials.user_name[:20]}
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas tentativas de login. Aguarde 1 minuto."
        )
    
    # Verificar brute force por usuário
    if check_brute_force(client_ip, credentials.user_name):
        log_security_event(
            "BRUTE_FORCE_DETECTED",
            "Brute force attempt blocked",
            ip_address=client_ip,
            extra_data={"username": credentials.user_name[:20]}
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Conta temporariamente bloqueada. Aguarde alguns minutos."
        )
    
    # Validar input contra SQL Injection
    is_safe, error_msg = check_input_safety(credentials.user_name, "nome de usuário")
    if not is_safe:
        log_security_event(
            "INJECTION_ATTEMPT",
            error_msg,
            ip_address=client_ip,
            extra_data={"username": credentials.user_name[:50]}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Caracteres inválidos no nome de usuário"
        )
    
    # Sanitizar username
    username_clean = sanitize_string(credentials.user_name, max_length=100)
    
    # Buscar usuário - usando parâmetros do ORM (protegido contra SQL injection)
    user = db.query(User).filter(User.user_name == username_clean).first()
    
    if not user:
        record_failed_attempt(client_ip, credentials.user_name)
        log_security_event(
            "LOGIN_FAILED",
            "User not found",
            ip_address=client_ip,
            extra_data={"username": credentials.user_name[:20]}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos"
        )
    
    # Verificar senha
    if not verify_password(credentials.senha, user.senha_hash):
        record_failed_attempt(client_ip, credentials.user_name)
        log_security_event(
            "LOGIN_FAILED",
            "Invalid password",
            user_id=user.id,
            ip_address=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos"
        )
    
    # Login bem sucedido - limpar tentativas falhas
    clear_failed_attempts(client_ip, credentials.user_name)
    
    # Criar token JWT
    token_data = {
        "id": user.id,
        "user_name": user.user_name,
        "planta": user.planta.value,
        "role": user.role.value
    }
    
    access_token = create_access_token(token_data)
    
    logger.info(f"Login successful for user: {user.user_name} from IP: {client_ip}")
    
    # Retornar token e dados do usuário
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            user_name=user.user_name,
            email=user.email,
            nome_completo=user.nome_completo,
            departamento=user.departamento,
            planta=user.planta,
            role=user.role,
            primeiro_login=user.primeiro_login
        )
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Retorna informações do usuário autenticado
    """
    return UserResponse(
        id=current_user.id,
        user_name=current_user.user_name,
        email=current_user.email,
        nome_completo=current_user.nome_completo,
        departamento=current_user.departamento,
        planta=current_user.planta,
        role=current_user.role,
        primeiro_login=current_user.primeiro_login
    )


from pydantic import BaseModel, Field

class AlterarSenhaRequest(BaseModel):
    senha_atual: str = Field(..., min_length=1)
    nova_senha: str = Field(..., min_length=6, max_length=128)
    confirmar_senha: str = Field(..., min_length=6, max_length=128)


@router.post("/alterar-senha")
def alterar_senha(
    dados: AlterarSenhaRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Permite ao usuário alterar sua própria senha
    """
    client_ip = get_client_ip(request)
    
    # Verificar se nova senha e confirmação são iguais
    if dados.nova_senha != dados.confirmar_senha:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nova senha e confirmação não coincidem"
        )
    
    # Verificar senha atual
    # Buscar usuário atual no banco
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    if not verify_password(dados.senha_atual, user.senha_hash):
        log_security_event(
            "PASSWORD_CHANGE_FAILED",
            "Senha atual incorreta",
            user_id=user.id,
            ip_address=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha atual incorreta"
        )
    
    # Verificar se nova senha é diferente da atual
    if verify_password(dados.nova_senha, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A nova senha deve ser diferente da senha atual"
        )
    
    # Atualizar senha e marcar que não é mais primeiro login
    user.senha_hash = hash_password(dados.nova_senha)
    user.primeiro_login = False
    db.commit()
    
    logger.info(f"Senha alterada com sucesso para usuário: {user.user_name} de IP: {client_ip}")
    log_security_event(
        "PASSWORD_CHANGED",
        "Senha alterada com sucesso",
        user_id=user.id,
        ip_address=client_ip
    )
    
    return {"message": "Senha alterada com sucesso", "primeiro_login": False}
