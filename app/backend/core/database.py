from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from .config import settings
import logging

logger = logging.getLogger(__name__)

# Engine do SQLAlchemy com pool otimizado para escalabilidade
engine = create_engine(
    settings.DATABASE_URL,
    # Pool de conexões otimizado
    poolclass=QueuePool,
    pool_size=10,           # Conexões mantidas no pool
    max_overflow=20,        # Conexões extras permitidas
    pool_timeout=30,        # Timeout para obter conexão
    pool_recycle=1800,      # Reciclar conexões a cada 30 min
    pool_pre_ping=True,     # Verificar conexão antes de usar
    echo=False,
    # Otimizações de conexão MySQL
    connect_args={
        "connect_timeout": 10,
        "read_timeout": 30,
        "write_timeout": 30,
    }
)

# Session local com configurações otimizadas
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Evita queries extras após commit
)

# Base para models
Base = declarative_base()


# Eventos de conexão para logging e debug
@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Log quando uma conexão é obtida do pool"""
    logger.debug("Conexão obtida do pool")


@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """Log quando uma conexão retorna ao pool"""
    logger.debug("Conexão retornada ao pool")


def get_db():
    """
    Dependência para obter sessão do banco.
    Usa context manager para garantir fechamento correto.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Erro na sessão do banco: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Inicializa o banco de dados (cria tabelas)"""
    Base.metadata.create_all(bind=engine)
    logger.info("Tabelas do banco de dados criadas/verificadas")


def get_pool_status() -> dict:
    """Retorna status atual do pool de conexões"""
    pool = engine.pool
    return {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "invalid": pool.invalidatedsize() if hasattr(pool, 'invalidatedsize') else 0
    }

