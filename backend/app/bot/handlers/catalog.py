# =============================================================================
# VimaBOT SaaS - Handler: Catálogo
# =============================================================================
# Gerencia a listagem e os detalhes de produtos do catálogo no Telegram.
# =============================================================================

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Product
from app.bot.keyboards import get_catalog_keyboard, get_product_details_keyboard
from app.bot.states import ShopStates

catalog_router = Router(name="catalog_router")


@catalog_router.callback_query(F.data == "shop_catalog")
async def show_catalog(callback: CallbackQuery, state: FSMContext, bot_tenant_id: str, db: AsyncSession):
    """
    Exibe a lista de produtos ativos do tenant.
    bot_tenant_id é injetado pelo BotManager via kwargs do dispatcher.
    db é injetado pelo DbSessionMiddleware.
    """
    await state.set_state(ShopStates.browsing)
    
    result = await db.execute(
        select(Product)
        .where(Product.tenant_id == bot_tenant_id, Product.is_active == True)
        .limit(10) # Para manter simples sem scroll na v1
    )
    products = result.scalars().all()
    
    keyboard = get_catalog_keyboard(products)
    
    if not products:
         msg = "📚 *Catálogo de Produtos*\n\nNão há produtos disponíveis no momento."
    else:
         msg = "📚 *Catálogo de Produtos*\n\nSelecione um produto para mais detalhes:"

    await callback.message.edit_text(
        msg,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await callback.answer()


@catalog_router.callback_query(F.data.startswith("prod_info:"))
async def show_product_details(callback: CallbackQuery, state: FSMContext, bot_tenant_id: str, db: AsyncSession):
    """Exibe os detalhes de um produto específico."""
    product_id = callback.data.split(":")[1]
    
    result = await db.execute(
        select(Product).where(Product.tenant_id == bot_tenant_id, Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        await callback.answer("Produto não encontrado.", show_alert=True)
        return

    keyboard = get_product_details_keyboard(str(product.id))
    
    await callback.message.edit_text(
        f"📦 *{product.name}* \n\n"
        f"💰 Valor: R$ {product.price:.2f}\n"
        f"📝 Descrição:\n{product.description}\n",
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await callback.answer()
