"""
Módulo de utilitários de segurança avançada.

Contém funções para:
- Sanitização de inputs contra SQL Injection e XSS
- Rate limiting
- Validação de entradas
- Logging de segurança
"""

import re
import html
import logging
from typing import Optional, Any
from functools import wraps
from datetime import datetime, timedelta
from collections import defaultdict
import threading

# Configurar logger de segurança
security_logger = logging.getLogger("security")
security_logger.setLevel(logging.WARNING)

# Rate limiting em memória (para produção usar Redis)
class RateLimiter:
    """
    Rate limiter em memória com janela deslizante.
    Para produção, considere usar Redis para escalabilidade horizontal.
    """
    
    def __init__(self):
        self._requests: dict = defaultdict(list)
        self._lock = threading.Lock()
    
    def is_allowed(
        self, 
        key: str, 
        max_requests: int = 100, 
        window_seconds: int = 60
    ) -> bool:
        """
        Verifica se a requisição deve ser permitida.
        
        Args:
            key: Identificador único (IP, user_id, etc.)
            max_requests: Número máximo de requisições
            window_seconds: Janela de tempo em segundos
            
        Returns:
            True se permitido, False se limite excedido
        """
        now = datetime.now()
        window_start = now - timedelta(seconds=window_seconds)
        
        with self._lock:
            # Limpar requisições antigas
            self._requests[key] = [
                req_time for req_time in self._requests[key]
                if req_time > window_start
            ]
            
            # Verificar limite
            if len(self._requests[key]) >= max_requests:
                security_logger.warning(
                    f"Rate limit exceeded for key: {key[:50]}... "
                    f"({len(self._requests[key])} requests in {window_seconds}s)"
                )
                return False
            
            # Registrar nova requisição
            self._requests[key].append(now)
            return True
    
    def get_remaining(self, key: str, max_requests: int = 100) -> int:
        """Retorna quantas requisições ainda são permitidas"""
        with self._lock:
            current = len(self._requests.get(key, []))
            return max(0, max_requests - current)
    
    def cleanup(self, max_age_seconds: int = 300):
        """Remove entradas antigas para liberar memória"""
        cutoff = datetime.now() - timedelta(seconds=max_age_seconds)
        with self._lock:
            keys_to_delete = []
            for key, timestamps in self._requests.items():
                self._requests[key] = [t for t in timestamps if t > cutoff]
                if not self._requests[key]:
                    keys_to_delete.append(key)
            for key in keys_to_delete:
                del self._requests[key]


# Instância global do rate limiter
rate_limiter = RateLimiter()


# Padrões de SQL Injection conhecidos
SQL_INJECTION_PATTERNS = [
    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|TRUNCATE|ALTER|CREATE|EXEC|EXECUTE)\b)",
    r"(--|\#|\/\*|\*\/)",  # Comentários SQL
    r"(\bOR\b\s+\d+\s*=\s*\d+)",  # OR 1=1
    r"(\bAND\b\s+\d+\s*=\s*\d+)",  # AND 1=1
    r"(\bUNION\b.*\bSELECT\b)",  # UNION SELECT
    r"(';|\"--|;--)",  # Terminadores
    r"(\bWAITFOR\b\s+\bDELAY\b)",  # Time-based
    r"(\bBENCHMARK\b\s*\()",  # MySQL benchmark
    r"(\bSLEEP\b\s*\()",  # MySQL sleep
    r"(\bLOAD_FILE\b\s*\()",  # File read
    r"(\bINTO\s+OUTFILE\b)",  # File write
    r"(\bINTO\s+DUMPFILE\b)",  # Binary file write
]

# Padrões de XSS conhecidos
XSS_PATTERNS = [
    r"<script[^>]*>",
    r"javascript:",
    r"on\w+\s*=",  # onclick, onerror, etc.
    r"<iframe[^>]*>",
    r"<object[^>]*>",
    r"<embed[^>]*>",
    r"<link[^>]*>",
    r"expression\s*\(",
    r"vbscript:",
    r"data:text/html",
]


def detect_sql_injection(value: str) -> bool:
    """
    Detecta possíveis tentativas de SQL Injection.
    
    Args:
        value: String a ser verificada
        
    Returns:
        True se detectado padrão suspeito
    """
    if not value:
        return False
    
    value_upper = value.upper()
    
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, value_upper, re.IGNORECASE):
            security_logger.warning(
                f"Possible SQL injection detected: {value[:100]}..."
            )
            return True
    
    return False


def detect_xss(value: str) -> bool:
    """
    Detecta possíveis tentativas de XSS.
    
    Args:
        value: String a ser verificada
        
    Returns:
        True se detectado padrão suspeito
    """
    if not value:
        return False
    
    value_lower = value.lower()
    
    for pattern in XSS_PATTERNS:
        if re.search(pattern, value_lower, re.IGNORECASE):
            security_logger.warning(
                f"Possible XSS detected: {value[:100]}..."
            )
            return True
    
    return False


def sanitize_string(
    value: Optional[str],
    max_length: int = 1000,
    allow_html: bool = False,
    strip_dangerous: bool = True
) -> Optional[str]:
    """
    Sanitiza uma string removendo caracteres perigosos.
    
    Args:
        value: String a ser sanitizada
        max_length: Tamanho máximo permitido
        allow_html: Se True, não escapa HTML
        strip_dangerous: Se True, remove padrões perigosos
        
    Returns:
        String sanitizada ou None
    """
    if value is None:
        return None
    
    if not isinstance(value, str):
        value = str(value)
    
    # Remover espaços extras
    value = value.strip()
    
    # Limitar tamanho
    if len(value) > max_length:
        value = value[:max_length]
    
    # Escapar HTML se necessário
    if not allow_html:
        value = html.escape(value)
    
    # Remover caracteres de controle (exceto newline e tab)
    value = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', value)
    
    # Remover padrões perigosos
    if strip_dangerous:
        # Remover null bytes
        value = value.replace('\x00', '')
        # Remover unicode perigoso
        value = re.sub(r'[\u200b-\u200f\u2028-\u202f\u2060-\u206f]', '', value)
    
    return value


def sanitize_numeric_string(value: Optional[str]) -> Optional[str]:
    """
    Sanitiza uma string que deveria conter apenas números.
    Remove tudo exceto dígitos.
    
    Args:
        value: String a ser sanitizada
        
    Returns:
        String contendo apenas dígitos ou None
    """
    if value is None:
        return None
    
    if not isinstance(value, str):
        value = str(value)
    
    # Remover tudo que não é dígito
    cleaned = re.sub(r'[^\d]', '', value.strip())
    
    return cleaned if cleaned else None


def sanitize_alphanumeric(
    value: Optional[str],
    allow_chars: str = "",
    max_length: int = 100
) -> Optional[str]:
    """
    Sanitiza uma string permitindo apenas caracteres alfanuméricos.
    
    Args:
        value: String a ser sanitizada
        allow_chars: Caracteres adicionais permitidos
        max_length: Tamanho máximo
        
    Returns:
        String sanitizada ou None
    """
    if value is None:
        return None
    
    if not isinstance(value, str):
        value = str(value)
    
    # Escapar caracteres especiais do regex
    escaped_chars = re.escape(allow_chars)
    pattern = f'[^a-zA-Z0-9{escaped_chars}]'
    
    cleaned = re.sub(pattern, '', value.strip())
    
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    
    return cleaned if cleaned else None


def validate_part_number(value: str) -> bool:
    """
    Valida formato de Part Number.
    Permite: letras, números, hífens, pontos e underscores.
    
    Args:
        value: Part number a validar
        
    Returns:
        True se válido
    """
    if not value:
        return False
    
    # Part number: alfanumérico com alguns caracteres especiais
    pattern = r'^[A-Za-z0-9\-_.]+$'
    return bool(re.match(pattern, value.strip()))


def validate_etiqueta(value: str) -> bool:
    """
    Valida formato de etiqueta de inventário.
    Deve ser numérica com até 5 dígitos.
    
    Args:
        value: Etiqueta a validar
        
    Returns:
        True se válido
    """
    if not value:
        return False
    
    # Etiqueta: apenas números, 1-5 dígitos
    pattern = r'^\d{1,5}$'
    return bool(re.match(pattern, value.strip()))


def validate_planta(value: str) -> bool:
    """
    Valida código de planta.
    
    Args:
        value: Código da planta
        
    Returns:
        True se válido
    """
    plantas_validas = {'PS01', 'PS02', 'PS03', 'PS05', 'PB82'}
    return value and value.upper() in plantas_validas


def validate_zona(value: str) -> bool:
    """
    Valida código de zona.
    
    Args:
        value: Código da zona
        
    Returns:
        True se válido
    """
    if not value:
        return False
    
    # Zona: uma letra maiúscula
    pattern = r'^[A-Za-z]$'
    return bool(re.match(pattern, value.strip()))


def log_security_event(
    event_type: str,
    message: str,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    extra_data: Optional[dict] = None
):
    """
    Registra um evento de segurança.
    
    Args:
        event_type: Tipo do evento (LOGIN_FAILED, INJECTION_ATTEMPT, etc.)
        message: Descrição do evento
        user_id: ID do usuário (se disponível)
        ip_address: Endereço IP
        extra_data: Dados adicionais
    """
    log_data = {
        "event_type": event_type,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "ip_address": ip_address,
    }
    
    if extra_data:
        log_data["extra"] = extra_data
    
    security_logger.warning(f"SECURITY_EVENT: {log_data}")


def check_input_safety(value: str, field_name: str = "input") -> tuple[bool, str]:
    """
    Verifica se um input é seguro.
    
    Args:
        value: Valor a verificar
        field_name: Nome do campo para mensagem de erro
        
    Returns:
        Tuple (is_safe, error_message)
    """
    if not value:
        return True, ""
    
    if detect_sql_injection(value):
        return False, f"Caracteres inválidos detectados no campo {field_name}"
    
    if detect_xss(value):
        return False, f"Conteúdo não permitido no campo {field_name}"
    
    return True, ""


# Decorador para rate limiting em endpoints
def rate_limit(
    max_requests: int = 100,
    window_seconds: int = 60,
    key_func=None
):
    """
    Decorador para aplicar rate limiting a uma função.
    
    Args:
        max_requests: Número máximo de requisições
        window_seconds: Janela de tempo em segundos
        key_func: Função para extrair a chave (ex: lambda request: request.client.host)
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extrair chave (padrão: nome da função)
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = func.__name__
            
            if not rate_limiter.is_allowed(key, max_requests, window_seconds):
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=429,
                    detail="Muitas requisições. Tente novamente em alguns instantes."
                )
            
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = func.__name__
            
            if not rate_limiter.is_allowed(key, max_requests, window_seconds):
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=429,
                    detail="Muitas requisições. Tente novamente em alguns instantes."
                )
            
            return func(*args, **kwargs)
        
        # Retornar wrapper apropriado
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator
