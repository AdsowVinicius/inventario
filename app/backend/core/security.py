from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .config import settings
from .database import get_db
from models.user import User
import logging

# Contexto para hash de senha
# Use PBKDF2-SHA256 to avoid bcrypt 72-byte limitations and possible
# compatibility issues with the installed bcrypt backend.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()


def _truncate_utf8_to_bytes(s: str, max_bytes: int = 72) -> str:
    """Trunca uma string preservando limites de caracteres UTF-8.

    Garante que o resultado tenha no máximo `max_bytes` bytes quando codificado em UTF-8.
    """
    b = bytearray()
    for ch in s:
        chb = ch.encode("utf-8")
        if len(b) + len(chb) > max_bytes:
            break
        b.extend(chb)
    return b.decode("utf-8", errors="ignore")


def hash_password(password: str) -> str:
    """Gera hash da senha.

    Trunca a senha para o limite de 72 bytes do bcrypt (UTF-8) para evitar
    erros do backend e garantir comportamento consistente.
    """
    try:
        pw_bytes_len = len(password.encode("utf-8"))
    except Exception:
        pw_bytes_len = None

    if pw_bytes_len is not None and pw_bytes_len > 72:
        logger.warning("Password length %s bytes exceeds bcrypt 72-byte limit; truncating.", pw_bytes_len)
        password = _truncate_utf8_to_bytes(password, 72)

    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha está correta"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria token JWT"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decodifica token JWT"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Obtém usuário atual a partir do token"""
    token = credentials.credentials
    payload = decode_token(token)
    
    user_id = payload.get("id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado"
        )
    
    return user


def require_role(*allowed_roles: str):
    """Dependência para verificar papel do usuário"""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para acessar este recurso"
            )
        return current_user
    return role_checker
