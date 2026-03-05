# =============================================================================
# VimaBOT SaaS - Handler: Catálogo
# =============================================================================
# Gerencia a listagem e os detalhes de produtos do catálogo no Telegram.
# =============================================================================

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

# Imports comentados por enquanto, pois o Product Service será criado depois
# from app.bot.keyboards import get_catalog_keyboard, get_product_details_keyboard
from app.bot.states import ShopStates

catalog_router = Router(name="catalog_router")


@catalog_router.callback_query(F.data == "shop_catalog")
async def show_catalog(callback: CallbackQuery, state: FSMContext, bot_tenant_id: str):
    """
    Exibe a lista de produtos ativos do tenant.
    bot_tenant_id é injetado pelo BotManager via kwargs do dispatcher.
    """
    await state.set_state(ShopStates.browsing)
    
    # Aqui vamos buscar os produtos no banco de dados usando o tenant_id
    # products = await ProductService.list_active_products(bot_tenant_id)
    # keyboard = get_catalog_keyboard(products)
    
    # Exemplo temporário para estrutura:
    await callback.message.edit_text(
        "📚 *Catálogo de Produtos*\n\n"
        "Aqui estão os produtos disponíveis (integração DB pendente):",
        parse_mode="Markdown",
        reply_markup=None  # será substituído por keyboard
    )
    await callback.answer()


@catalog_router.callback_query(F.data.startswith("cat_page:"))
async def change_catalog_page(callback: CallbackQuery, state: FSMContext, bot_tenant_id: str):
    """Muda a página da listagem de produtos."""
    page = int(callback.data.split(":")[1])
    
    # Busca a página específica
    # products = await ProductService.list_active_products(bot_tenant_id, page=page)
    # keyboard = get_catalog_keyboard(products, page=page, total_pages=X)
    
    await callback.message.edit_text(
        f"📚 *Catálogo de Produtos - Página {page}*\n\n(Integração pendente)",
        parse_mode="Markdown"
    )
    await callback.answer()


@catalog_router.callback_query(F.data.startswith("prod_info:"))
async def show_product_details(callback: CallbackQuery, state: FSMContext, bot_tenant_id: str):
    """Exibe os detalhes de um produto específico."""
    product_id = callback.data.split(":")[1]
    
    # Busca detalhes
    # product = await ProductService.get_product(bot_tenant_id, product_id)
    # keyboard = get_product_details_keyboard(product_id)
    
    await callback.message.edit_text(
        f"📦 *Detalhes do Produto* \n\n"
        f"ID: `{product_id}`\n\n(Integração pendente)",
        parse_mode="Markdown"
    )
    await callback.answer()
