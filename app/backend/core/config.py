from pydantic_settings import BaseSettings
from typing import Optional, List, Union


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Banco de Dados
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/inventario"
    
    # JWT
    SECRET_KEY: str = "sua-chave-secreta-super-segura-mude-isso-em-producao"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 horas
    
    # CORS
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://localhost:5173"
    
    @property
    def cors_origins(self) -> List[str]:
        if isinstance(self.BACKEND_CORS_ORIGINS, str):
            return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]
        return self.BACKEND_CORS_ORIGINS
    
    # Aplicação
    PROJECT_NAME: str = "Sistema de Inventário"
    VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
