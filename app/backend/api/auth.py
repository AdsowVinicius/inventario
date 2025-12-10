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
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth", tags=["Autenticação"])
logger = logging.getLogger(__name__)

# ============================================================
# SISTEMA DE BLOQUEIO PROGRESSIVO
# ============================================================
# Estrutura: {username: {attempts, lock_until, lock_cycles}}
_login_tracker: dict = {}

# Configurações
MAX_ATTEMPTS = 5  # Tentativas antes de bloquear
LOCK_DURATION_MINUTES = 2  # Tempo de bloqueio inicial
MAX_LOCK_CYCLES = 3  # Após isso, bloqueio permanente


def get_client_ip(request: Request) -> str:
    """Obtém IP do cliente considerando proxy"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def get_user_lock_status(username: str) -> dict:
    """
    Retorna status de bloqueio do usuário.
    Retorna: {is_locked, remaining_seconds, attempts, remaining_attempts, lock_cycles, is_permanent}
    """
    if username not in _login_tracker:
        return {
            "is_locked": False,
            "remaining_seconds": 0,
            "attempts": 0,
            "remaining_attempts": MAX_ATTEMPTS,
            "lock_cycles": 0,
            "is_permanent": False
        }
    
    tracker = _login_tracker[username]
    lock_until = tracker.get("lock_until")
    lock_cycles = tracker.get("lock_cycles", 0)
    attempts = tracker.get("attempts", 0)
    
    # Verificar se bloqueio expirou
    if lock_until:
        now = datetime.now()
        if now < lock_until:
            remaining = (lock_until - now).total_seconds()
            return {
                "is_locked": True,
                "remaining_seconds": int(remaining),
                "attempts": attempts,
                "remaining_attempts": 0,
                "lock_cycles": lock_cycles,
                "is_permanent": False
            }
        else:
            # Bloqueio expirou - resetar tentativas mas manter ciclos
            tracker["attempts"] = 0
            tracker["lock_until"] = None
    
    return {
        "is_locked": False,
        "remaining_seconds": 0,
        "attempts": tracker.get("attempts", 0),
        "remaining_attempts": MAX_ATTEMPTS - tracker.get("attempts", 0),
        "lock_cycles": lock_cycles,
        "is_permanent": False
    }


def record_failed_attempt(username: str) -> dict:
    """
    Registra tentativa falha e retorna status atualizado.
    Retorna info sobre bloqueio se aplicável.
    """
    if username not in _login_tracker:
        _login_tracker[username] = {"attempts": 0, "lock_until": None, "lock_cycles": 0}
    
    tracker = _login_tracker[username]
    tracker["attempts"] = tracker.get("attempts", 0) + 1
    
    result = {
        "attempts": tracker["attempts"],
        "remaining_attempts": MAX_ATTEMPTS - tracker["attempts"],
        "is_locked": False,
        "lock_duration_minutes": 0,
        "lock_cycles": tracker.get("lock_cycles", 0),
        "is_permanent_lock": False
    }
    
    # Verificar se atingiu limite de tentativas
    if tracker["attempts"] >= MAX_ATTEMPTS:
        tracker["lock_cycles"] = tracker.get("lock_cycles", 0) + 1
        lock_cycles = tracker["lock_cycles"]
        
        # Bloqueio progressivo: 2min, 4min, 6min...
        lock_minutes = LOCK_DURATION_MINUTES * lock_cycles
        tracker["lock_until"] = datetime.now() + timedelta(minutes=lock_minutes)
        tracker["attempts"] = 0  # Reset para próximo ciclo
        
        result["is_locked"] = True
        result["lock_duration_minutes"] = lock_minutes
        result["lock_cycles"] = lock_cycles
        result["remaining_attempts"] = 0
        
        # Verificar se excedeu ciclos máximos
        if lock_cycles >= MAX_LOCK_CYCLES:
            result["is_permanent_lock"] = True
    
    return result


def clear_login_tracker(username: str):
    """Limpa tracker após login bem sucedido"""
    if username in _login_tracker:
        del _login_tracker[username]


def admin_unlock_user(username: str):
    """Admin desbloqueia usuário (limpa tracker e bloqueio permanente)"""
    if username in _login_tracker:
        del _login_tracker[username]


@router.post("/login", response_model=TokenResponse)
def login(
    credentials: UserLogin, 
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Endpoint de login com proteções contra brute force
    Sistema de bloqueio progressivo:
    - 5 tentativas -> bloqueio 2 minutos
    - 5 tentativas -> bloqueio 4 minutos  
    - 5 tentativas -> bloqueio 6 minutos + bloqueio permanente (só admin desbloqueia)
    """
    client_ip = get_client_ip(request)
    username_clean = sanitize_string(credentials.user_name, max_length=100)
    
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
    
    # Buscar usuário primeiro para verificar bloqueio permanente
    user = db.query(User).filter(User.user_name == username_clean).first()
    
    # Verificar bloqueio permanente no banco de dados
    if user and user.bloqueado_permanente:
        log_security_event(
            "LOGIN_BLOCKED_PERMANENT",
            "User permanently blocked",
            user_id=user.id,
            ip_address=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta bloqueada permanentemente. Entre em contato com um administrador."
        )
    
    # Verificar bloqueio temporário
    lock_status = get_user_lock_status(username_clean)
    if lock_status["is_locked"]:
        minutes = lock_status["remaining_seconds"] // 60
        seconds = lock_status["remaining_seconds"] % 60
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Conta temporariamente bloqueada. Aguarde {minutes}min {seconds}s."
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
    
    # Usuário não encontrado
    if not user:
        lock_result = record_failed_attempt(username_clean)
        remaining = lock_result["remaining_attempts"]
        
        log_security_event(
            "LOGIN_FAILED",
            "User not found",
            ip_address=client_ip,
            extra_data={"username": credentials.user_name[:20]}
        )
        
        if lock_result["is_locked"]:
            if lock_result["is_permanent_lock"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Conta bloqueada permanentemente após {MAX_LOCK_CYCLES} ciclos. Entre em contato com um administrador."
                )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Muitas tentativas falhas. Conta bloqueada por {lock_result['lock_duration_minutes']} minutos."
            )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Usuário ou senha incorretos. Restam {remaining} tentativas."
        )
    
    # Verificar senha
    if not verify_password(credentials.senha, user.senha_hash):
        lock_result = record_failed_attempt(username_clean)
        remaining = lock_result["remaining_attempts"]
        
        log_security_event(
            "LOGIN_FAILED",
            "Invalid password",
            user_id=user.id,
            ip_address=client_ip
        )
        
        if lock_result["is_locked"]:
            if lock_result["is_permanent_lock"]:
                # Marcar como bloqueado permanente no banco
                user.bloqueado_permanente = True
                db.commit()
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Conta bloqueada permanentemente após {MAX_LOCK_CYCLES} ciclos de tentativas. Entre em contato com um administrador."
                )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Muitas tentativas falhas. Conta bloqueada por {lock_result['lock_duration_minutes']} minutos. (Ciclo {lock_result['lock_cycles']}/{MAX_LOCK_CYCLES})"
            )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Usuário ou senha incorretos. Restam {remaining} tentativas."
        )
    
    # Login bem sucedido - limpar tracker
    clear_login_tracker(username_clean)
    
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


# ============================================================
# ENDPOINT PARA ADMIN DESBLOQUEAR USUÁRIO
# ============================================================
from core.security import require_role

@router.post("/desbloquear/{user_id}")
def desbloquear_usuario(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN"))
):
    """
    Desbloqueia um usuário bloqueado.
    Apenas ADMIN pode usar este endpoint.
    Remove bloqueio permanente do banco e limpa o tracker de tentativas.
    """
    client_ip = get_client_ip(request)
    
    # Buscar usuário a ser desbloqueado
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Limpar bloqueio permanente no banco
    was_blocked = user.bloqueado_permanente
    user.bloqueado_permanente = False
    db.commit()
    
    # Limpar tracker de tentativas na memória
    admin_unlock_user(user.user_name)
    
    log_security_event(
        "USER_UNLOCKED",
        f"User {user.user_name} unlocked by admin {current_user.user_name}",
        user_id=user.id,
        ip_address=client_ip
    )
    
    logger.info(f"Usuário {user.user_name} desbloqueado por {current_user.user_name}")
    
    return {
        "message": f"Usuário {user.user_name} desbloqueado com sucesso",
        "was_permanently_blocked": was_blocked
    }


@router.get("/status-bloqueio/{username}")
def verificar_status_bloqueio(
    username: str,
    current_user: User = Depends(require_role("ADMIN"))
):
    """
    Verifica status de bloqueio de um usuário.
    Apenas ADMIN pode usar este endpoint.
    """
    username_clean = sanitize_string(username, max_length=100)
    status = get_user_lock_status(username_clean)
    
    return {
        "username": username_clean,
        "is_temporarily_locked": status["is_locked"],
        "remaining_seconds": status["remaining_seconds"],
        "attempts": status["attempts"],
        "remaining_attempts": status["remaining_attempts"],
        "lock_cycles": status["lock_cycles"],
        "max_cycles_before_permanent": MAX_LOCK_CYCLES
    }


@router.get("/status-bloqueios-todos")
def listar_todos_status_bloqueio(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN"))
):
    """
    Lista status de bloqueio de todos os usuários.
    Retorna um dicionário com username como chave.
    Apenas ADMIN pode usar este endpoint.
    """
    # Buscar todos os usuários
    usuarios = db.query(User).all()
    
    resultado = {}
    for user in usuarios:
        status = get_user_lock_status(user.user_name)
        resultado[user.user_name] = {
            "user_id": user.id,
            "is_temporarily_locked": status["is_locked"],
            "remaining_seconds": status["remaining_seconds"],
            "attempts": status["attempts"],
            "remaining_attempts": status["remaining_attempts"],
            "lock_cycles": status["lock_cycles"],
            "is_permanently_blocked": user.bloqueado_permanente
        }
    
    return resultado
