from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from core.config import settings
from core.database import init_db, get_pool_status
from core.security_utils import rate_limiter, log_security_event
from api import auth_router, itens_router, contagem_router, exportacao_router, users_router, dashboard_router
import logging
import time
from datetime import datetime
import pytz

# Fuso horário de Brasília
BRAZIL_TZ = pytz.timezone('America/Sao_Paulo')

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware para adicionar headers de segurança"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Headers de segurança
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware para rate limiting global"""
    
    async def dispatch(self, request: Request, call_next):
        # Obter IP do cliente
        client_ip = request.client.host if request.client else "unknown"
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        
        # Configurar limites por tipo de endpoint
        path = request.url.path
        
        # Login tem limite mais restrito (anti brute-force)
        if "/auth/login" in path:
            max_requests = 10
            window = 60
        # APIs de busca podem ter mais requisições
        elif "/buscar" in path or "/sugerir" in path:
            max_requests = 200
            window = 60
        # Limite padrão
        else:
            max_requests = 100
            window = 60
        
        # Verificar rate limit
        key = f"{client_ip}:{path}"
        if not rate_limiter.is_allowed(key, max_requests, window):
            log_security_event(
                "RATE_LIMIT_EXCEEDED",
                f"Rate limit exceeded for {path}",
                ip_address=client_ip
            )
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Muitas requisições. Aguarde alguns instantes.",
                    "retry_after": window
                },
                headers={"Retry-After": str(window)}
            )
        
        return await call_next(request)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging de requisições"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Processar requisição
        response = await call_next(request)
        
        # Calcular tempo de resposta
        process_time = time.time() - start_time
        
        # Log apenas para requisições lentas ou com erro
        if process_time > 1.0 or response.status_code >= 400:
            client_ip = request.client.host if request.client else "unknown"
            logger.info(
                f"{request.method} {request.url.path} "
                f"- Status: {response.status_code} "
                f"- Time: {process_time:.3f}s "
                f"- IP: {client_ip}"
            )
        
        # Adicionar header de tempo de processamento
        response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
        
        return response


# Criar aplicação FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Sistema de Inventário - API Backend",
    docs_url="/docs" if settings.VERSION != "production" else None,
    redoc_url="/redoc" if settings.VERSION != "production" else None,
)

# Adicionar middlewares (ordem importa: primeiro adicionado = último executado)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    max_age=600,  # Cache preflight por 10 minutos
)

# Incluir routers
app.include_router(auth_router)
app.include_router(itens_router)
app.include_router(contagem_router)
app.include_router(exportacao_router)
app.include_router(users_router)
app.include_router(dashboard_router)


@app.on_event("startup")
def on_startup():
    """Executar na inicialização"""
    logger.info("🚀 Inicializando aplicação...")
    logger.info("📦 Criando tabelas no banco de dados...")
    init_db()
    try:
        logger.info(f"🔒 CORS origins loaded: {settings.cors_origins}")
    except Exception:
        logger.warning("🔒 CORS origins: (erro ao ler settings)")
    logger.info("✅ Aplicação iniciada com sucesso!")


@app.on_event("shutdown")
def on_shutdown():
    """Executar no encerramento"""
    logger.info("🛑 Encerrando aplicação...")
    # Limpar rate limiter
    rate_limiter.cleanup(0)
    logger.info("✅ Aplicação encerrada")


@app.get("/")
def root():
    """Endpoint raiz"""
    return {
        "mensagem": "API do Sistema de Inventário",
        "versao": settings.VERSION,
        "status": "online",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
def health_check():
    """Health check com status do pool de conexões"""
    try:
        pool_status = get_pool_status()
        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "database_pool": pool_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "degraded",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


@app.get("/metrics")
def metrics():
    """Métricas básicas do sistema (apenas para monitoramento)"""
    return {
        "timestamp": datetime.now().isoformat(),
        "database_pool": get_pool_status(),
        "rate_limiter_keys": len(rate_limiter._requests)
    }


# Handler global de exceções
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para exceções não tratadas"""
    client_ip = request.client.host if request.client else "unknown"
    
    log_security_event(
        "UNHANDLED_EXCEPTION",
        str(exc),
        ip_address=client_ip,
        extra_data={"path": str(request.url.path), "method": request.method}
    )
    
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=1,  # Para desenvolvimento; em produção usar mais workers
        access_log=True
    )

