# =============================================================================
# VimaBOT SaaS - Aplicação FastAPI Principal
# =============================================================================
# Ponto de entrada da API. Este arquivo contém a configuração inicial do
# FastAPI com os eventos de ciclo de vida (startup/shutdown) para
# inicializar e encerrar o banco de dados.
#
# A Fase 2 expandirá este arquivo com rotas, middlewares e autenticação.
#
# Uso:
#   uvicorn app.main:app --reload
# =============================================================================

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db, close_db


# =============================================================================
# Ciclo de Vida da Aplicação (Lifespan)
# =============================================================================
# O lifespan gerencia os eventos de startup e shutdown da aplicação.
# - Startup: Inicializa o banco de dados (cria tabelas se não existem).
# - Shutdown: Fecha conexões do pool de banco de dados.
# =============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação FastAPI.

    No startup:
        - Cria as tabelas do banco de dados (se não existirem).
        - Em produção, use Alembic para migrações.

    No shutdown:
        - Fecha o pool de conexões do banco de dados.
    """
    # --- STARTUP ---
    print(f"🚀 Iniciando {settings.app_name}...")
    print(f"📊 Ambiente: {settings.app_env}")
    print(f"🗄️  Banco: {settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}")

    # Cria as tabelas do banco (CREATE IF NOT EXISTS)
    await init_db()
    print("✅ Banco de dados inicializado com sucesso!")

    # Entrega o controle para a aplicação
    yield

    # --- SHUTDOWN ---
    print(f"🛑 Encerrando {settings.app_name}...")
    await close_db()
    print("✅ Conexões do banco de dados encerradas.")


# =============================================================================
# Instância Principal do FastAPI
# =============================================================================
app = FastAPI(
    title=settings.app_name,
    description=(
        "Plataforma multi-tenant para venda de produtos digitais via Telegram. "
        "Cada tenant gerencia seu próprio bot, catálogo e pagamentos PIX."
    ),
    version="0.1.0",
    lifespan=lifespan,
    # Docs disponíveis apenas em desenvolvimento
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
)


# =============================================================================
# Middleware CORS
# =============================================================================
# Permite que o frontend React (rodando em outra porta) acesse a API.
# Em produção, restrinja os origins para o domínio real.
# =============================================================================
app.add_middleware(
    CORSMiddleware,
    # Em desenvolvimento, aceita qualquer origin. Em produção, especifique os domínios.
    allow_origins=["*"] if settings.is_development else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Rota de Health Check
# =============================================================================
@app.get(
    "/health",
    tags=["Sistema"],
    summary="Verificação de saúde da API",
    description="Retorna o status da API para monitoramento e healthchecks.",
)
async def health_check():
    """
    Endpoint de health check para monitoramento.

    Retorna o status da API, nome da aplicação e ambiente atual.
    Usado pelo Docker healthcheck e por ferramentas de monitoramento.
    """
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": "0.1.0",
        "environment": settings.app_env,
    }
