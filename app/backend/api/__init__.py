# Importar todas as rotas
from .auth import router as auth_router
from .itens import router as itens_router
from .contagem import router as contagem_router
from .exportacao import router as exportacao_router
from .users import router as users_router

__all__ = ["auth_router", "itens_router", "contagem_router", "exportacao_router", "users_router"]
