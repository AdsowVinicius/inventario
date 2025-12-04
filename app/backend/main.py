from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.database import init_db
from api import auth_router, itens_router, contagem_router, exportacao_router, users_router, dashboard_router

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Sistema de Inventário - API Backend"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    print("🚀 Inicializando aplicação...")
    print("📦 Criando tabelas no banco de dados...")
    init_db()
    # Debug: mostrar origens CORS carregadas
    try:
        print(f"🔒 CORS origins loaded: {settings.cors_origins}")
    except Exception:
        print("🔒 CORS origins: (erro ao ler settings)")
    print("✅ Aplicação iniciada com sucesso!")


@app.get("/")
def root():
    """Endpoint raiz"""
    return {
        "mensagem": "API do Sistema de Inventário",
        "versao": settings.VERSION,
        "status": "online"
    }


@app.get("/health")
def health_check():
    """Health check"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
