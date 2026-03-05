# =============================================================================
# VimaBOT SaaS - Bot Manager (Multi-Bot)
# =============================================================================
# Gerencia múltiplas instâncias de bots simultaneamente.
# Permite iniciar e parar bots dinamicamente sem reiniciar a aplicação.
# Injeta o tenant_id no fluxo do aiogram para que os handlers saibam a
# qual loja o usuário pertence.
# =============================================================================

import asyncio
from typing import Dict
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.bot.handlers.start import start_router
from app.bot.handlers.catalog import catalog_router
from app.bot.handlers.cart import cart_router
from app.bot.handlers.payment import payment_router

logger = logging.getLogger(__name__)


class BotManager:
    """
    Gerenciador singleton para instâncias do aiogram.
    Mantém registro dos bots em execução e permite manipulação dinâmica.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BotManager, cls).__new__(cls)
            cls._instance.bots: Dict[str, Bot] = {}       # tenant_id -> Bot
            cls._instance.tasks: Dict[str, asyncio.Task] = {} # tenant_id -> Task
            cls._instance.dp = Dispatcher()
            
            # Registra os routers
            cls._instance.dp.include_router(start_router)
            cls._instance.dp.include_router(catalog_router)
            cls._instance.dp.include_router(cart_router)
            cls._instance.dp.include_router(payment_router)
            
        return cls._instance

    @classmethod
    def get_instance(cls) -> "BotManager":
        return cls()

    async def start_bot(self, tenant_id: str, bot_token: str) -> bool:
        """
        Inicia uma instância de bot para um tenant específico.
        Se já estiver rodando, retorna False.
        """
        if tenant_id in self.bots:
            logger.info(f"Bot_Manager: Bot do tenant {tenant_id} já está em execução.")
            return False
            
        try:
            bot = Bot(
                token=bot_token,
                default=DefaultBotProperties(parse_mode=ParseMode.HTML)
            )
            
            # Task para o long polling
            # Em produção, a injeção do tenant_id precisa ser passada para os handlers.
            # No aiogram v3 podemos passar pelo kwargs do start_polling
            task = asyncio.create_task(
                self.dp.start_polling(bot, bot_tenant_id=tenant_id)
            )
            
            self.bots[tenant_id] = bot
            self.tasks[tenant_id] = task
            logger.info(f"Bot_Manager: Bot iniciado para o tenant {tenant_id}")
            return True
            
        except Exception as e:
            logger.error(f"Bot_Manager: Erro ao iniciar bot do tenant {tenant_id}: {e}")
            return False

    async def stop_bot(self, tenant_id: str) -> bool:
        """
        Para e remove a instância de bot de um tenant.
        """
        if tenant_id not in self.bots:
            logger.warning(f"Bot_Manager: Bot do tenant {tenant_id} não está rodando.")
            return False
            
        try:
            bot = self.bots.pop(tenant_id)
            task = self.tasks.pop(tenant_id)
            
            # Fecha a sessão do bot e cancela a task de polling
            await bot.session.close()
            task.cancel()
            
            logger.info(f"Bot_Manager: Bot parado para o tenant {tenant_id}")
            return True
            
        except Exception as e:
            logger.error(f"Bot_Manager: Erro ao parar bot do tenant {tenant_id}: {e}")
            return False

    def is_running(self, tenant_id: str) -> bool:
        """Verifica se o bot do tenant está ativo no gerenciador."""
        return tenant_id in self.bots

    async def stop_all(self):
        """Para todos os bots (útil no shutdown da aplicação)."""
        tenant_ids = list(self.bots.keys())
        for tenant_id in tenant_ids:
            await self.stop_bot(tenant_id)


# Instância global
bot_manager = BotManager()
