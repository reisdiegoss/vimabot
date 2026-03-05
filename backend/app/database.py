# =============================================================================
# VimaBOT SaaS - Conexão com o Banco de Dados
# =============================================================================
# Módulo responsável por criar e gerenciar a conexão assíncrona com o
# PostgreSQL usando SQLAlchemy 2.0 Async.
#
# Componentes:
# - Engine Assíncrono: Gerencia o pool de conexões com o PostgreSQL.
# - AsyncSession: Sessões de banco de dados para operações ORM.
# - get_db(): Dependency injection para rotas FastAPI.
# - init_db(): Cria todas as tabelas no banco de dados.
# =============================================================================

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator

from app.config import settings


# =============================================================================
# Base Declarativa do SQLAlchemy
# =============================================================================
# Todas as classes de modelo (tabelas) herdam desta base.
# Ela fornece o mapeamento ORM e os metadados do schema.
# =============================================================================
class Base(DeclarativeBase):
    """
    Classe base para todos os modelos SQLAlchemy da aplicação.

    Todos os modelos de tabela devem herdar desta classe para serem
    registrados no metadata e criados automaticamente pelo init_db().
    """
    pass


# =============================================================================
# Engine Assíncrono
# =============================================================================
# O engine gerencia o pool de conexões com o banco de dados.
# Configurações:
# - echo: Loga as queries SQL no console (útil em desenvolvimento).
# - pool_size: Número de conexões mantidas no pool.
# - max_overflow: Conexões extras além do pool_size em picos de carga.
# - pool_pre_ping: Testa a conexão antes de usar (evita conexões mortas).
# =============================================================================
engine: AsyncEngine = create_async_engine(
    # URL de conexão do PostgreSQL com driver assíncrono asyncpg
    settings.database_url,
    # Loga as queries SQL apenas em ambiente de desenvolvimento
    echo=settings.is_development,
    # Pool de 5 conexões permanentes + até 10 extras em picos
    pool_size=5,
    max_overflow=10,
    # Testa se a conexão está viva antes de cada uso
    pool_pre_ping=True,
    # Timeout de 30 segundos para reciclar conexões ociosas
    pool_recycle=1800,
)


# =============================================================================
# Fábrica de Sessões Assíncronas
# =============================================================================
# async_sessionmaker cria sessões de banco de dados otimizadas para uso
# com async/await. Cada sessão é uma transação isolada que deve ser
# commitada ou revertida ao final do uso.
#
# Configurações:
# - autocommit=False: Transações manuais (controle explícito de commit).
# - autoflush=False: Flush manual (melhor performance em operações batch).
# - expire_on_commit=False: Objetos não expiram após commit (evita queries
#   extras ao acessar atributos após o commit).
# =============================================================================
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# =============================================================================
# Dependency Injection para FastAPI
# =============================================================================
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Gera uma sessão de banco de dados para uso nas rotas do FastAPI.

    Esta função é um generator assíncrono usado como dependência (Depends)
    nas rotas. Ela garante que a sessão seja fechada ao final de cada
    requisição, mesmo que ocorra um erro.

    Uso nas rotas:
        @router.get("/exemplo")
        async def minha_rota(db: AsyncSession = Depends(get_db)):
            resultado = await db.execute(select(MeuModelo))
            return resultado.scalars().all()

    Yields:
        AsyncSession: Sessão assíncrona do banco de dados.
    """
    async with async_session_factory() as session:
        try:
            # Disponibiliza a sessão para a rota
            yield session
            # Se a rota completou sem erros, faz commit das alterações
            await session.commit()
        except Exception:
            # Se houve erro, reverte todas as alterações da transação
            await session.rollback()
            # Re-lança a exceção para o FastAPI tratar (retornar 500, etc.)
            raise
        finally:
            # Garante que a sessão é fechada independente do resultado
            await session.close()


# =============================================================================
# Inicialização do Banco de Dados
# =============================================================================
async def init_db() -> None:
    """
    Cria todas as tabelas definidas nos modelos SQLAlchemy.

    Esta função deve ser chamada na inicialização da aplicação (startup event).
    Ela usa o metadata coletado de todos os modelos que herdam de Base para
    criar as tabelas correspondentes no PostgreSQL.

    IMPORTANTE:
    - Em produção, use Alembic para migrações em vez desta função.
    - Esta função é útil apenas para desenvolvimento e testes.
    - Ela NÃO exclui tabelas existentes (CREATE IF NOT EXISTS).
    """
    async with engine.begin() as conn:
        # Importa os modelos para garantir que estão registrados no metadata.
        # Sem este import, Base.metadata não conhece as tabelas.
        from app import models  # noqa: F401

        # Cria todas as tabelas que ainda não existem no banco
        await conn.run_sync(Base.metadata.create_all)


# =============================================================================
# Encerramento do Engine (Cleanup)
# =============================================================================
async def close_db() -> None:
    """
    Fecha o engine e libera todas as conexões do pool.

    Esta função deve ser chamada no shutdown event da aplicação para
    liberar recursos do pool de conexões de forma limpa.
    """
    await engine.dispose()
