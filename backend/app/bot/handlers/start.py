# =============================================================================
# VimaBOT SaaS - Handler: Start
# =============================================================================
# Gerencia o comando /start e exibe o menu principal.
# =============================================================================

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.bot.keyboards import get_main_menu
from app.bot.states import ShopStates

# Este router será anexado ao dispatcher principal no gerente.
start_router = Router(name="start_router")


@start_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, bot_tenant_id: str):
    """
    Handler para o comando /start.
    bot_tenant_id é injetado via middleware do BotManager.
    """
    await state.clear()
    
    welcome_text = (
        "👋 Olá! Bem-vindo(a) à nossa loja virtual.\n\n"
        "Selecione uma opção abaixo para começar:"
    )
    
    await message.answer(welcome_text, reply_markup=get_main_menu())


@start_router.callback_query(F.data == "main_menu")
async def process_main_menu(callback: CallbackQuery, state: FSMContext):
    """Volta para o menu principal a partir de qualquer lugar."""
    await state.clear()
    
    welcome_text = (
        "🏠 *Menu Principal*\n\n"
        "Selecione uma opção abaixo:"
    )
    
    await callback.message.edit_text(welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")
    await callback.answer()
