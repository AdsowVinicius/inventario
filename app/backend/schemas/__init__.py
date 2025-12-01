# Importar todos os schemas
from .user import UserBase, UserCreate, UserResponse, UserLogin, TokenResponse
from .itens import ItensInventarioBase, ItensInventarioCreate, ItensInventarioResponse, PartNumberResponse
from .contagem import (
    ContagemBase, ContagemCreate, ContagemResponse, 
    ContagemSugestaoResponse, ContagemFiltros, MessageResponse
)

__all__ = [
    "UserBase", "UserCreate", "UserResponse", "UserLogin", "TokenResponse",
    "ItensInventarioBase", "ItensInventarioCreate", "ItensInventarioResponse", "PartNumberResponse",
    "ContagemBase", "ContagemCreate", "ContagemResponse", 
    "ContagemSugestaoResponse", "ContagemFiltros", "MessageResponse"
]
