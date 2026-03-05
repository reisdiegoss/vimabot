# =============================================================================
# VimaBOT SaaS - Middleware: Database Session
# =============================================================================
# Injeta uma sessão de banco de dados do SQLAlchemy assíncrona
# em cada requisição (Message, CallbackQuery, etc.) que chega no bot.
# E também garante o isolamento commitando ou dando rollback ao final.
# =============================================================================

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.database import async_session_factory


class DbSessionMiddleware(BaseMiddleware):
    """
    Middleware que abre e gerencia o clico de vida de uma sessão assíncrona
    do SQLAlchemy para o Telegram Bot. Ele a adiciona como chave `db`
    na estrutura kwargs do aiogram, permitindo acesso dentro dos Handlers.
    """
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Pega do factory uma nova sessão 
        async with async_session_factory() as session:
            # Injeta ela (Dependency Injection manual do aiogram)
            data["db"] = session
            
            try:
                # Executa os demais middlewares e eventualmente atinge o Handler
                result = await handler(event, data)
                
                # Se algo foi alterado no BD sem erro nos fluxos, salva permanentemente
                await session.commit()
                return result
            except Exception as e:
                # Segurança caso ocorra um 500 no processamento do bot
                await session.rollback()
                raise e
