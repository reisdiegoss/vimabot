# =============================================================================
# VimaBOT SaaS - Aplicação FastAPI Principal
# =============================================================================
# Ponto de entrada da API com registro de todos os routers,
# middlewares e eventos de ciclo de vida.
# =============================================================================

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db, close_db, async_session_factory
from app.services.seed import seed_superadmin

from app.routers import auth, tenants, products, orders, bot_configs, bot_management
from app.bot.manager import bot_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia startup e shutdown da aplicação."""
    print(f"🚀 Iniciando {settings.app_name}...")
    print(f"📊 Ambiente: {settings.app_env}")
    print(f"🗄️  Banco: {settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}")

    await init_db()
    print("✅ Banco de dados inicializado!")

    async with async_session_factory() as session:
        await seed_superadmin(session)

    yield

    print(f"🛑 Encerrando {settings.app_name}...")
    await bot_manager.stop_all()  # Desliga todos os bots em andamento
    await close_db()
    print("✅ Conexões encerradas.")


app = FastAPI(
    title=settings.app_name,
    description=(
        "Plataforma multi-tenant para venda de produtos digitais via Telegram. "
        "Cada tenant gerencia seu próprio bot, catálogo e pagamentos PIX."
    ),
    version="0.3.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.is_development else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de todos os routers da API
app.include_router(auth.router)
app.include_router(tenants.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(bot_configs.router)
app.include_router(bot_management.router)


@app.get("/health", tags=["Sistema"], summary="Health check")
async def health_check():
    """Endpoint de verificação de saúde da API."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": "0.2.0",
        "environment": settings.app_env,
    }
