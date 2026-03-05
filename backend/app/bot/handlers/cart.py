# =============================================================================
# VimaBOT SaaS - Handler: Carrinho
# =============================================================================
# Gerencia o carrinho de compras salvo em memória no estado (FSM).
# =============================================================================

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

# from app.bot.keyboards import get_cart_keyboard
from app.bot.states import ShopStates

cart_router = Router(name="cart_router")


@cart_router.callback_query(F.data.startswith("add_cart:"))
async def add_to_cart(callback: CallbackQuery, state: FSMContext, bot_tenant_id: str):
    """Adiciona um produto ao carrinho (salvo no FSMContext)."""
    product_id = callback.data.split(":")[1]
    
    # Recupera o estado atual
    data = await state.get_data()
    cart = data.get("cart", [])
    
    # No futuro, verificar se o produto existe e adicionar ID + Nome + Preço
    cart.append(product_id)
    
    await state.update_data(cart=cart)
    
    await callback.answer("✅ Adicionado ao carrinho!", show_alert=True)
    # Poderíamos redirecionar para o menu principal ou visualizar carrinho
    
    
@cart_router.callback_query(F.data == "shop_cart")
async def view_cart(callback: CallbackQuery, state: FSMContext):
    """Exibe o conteúdo do carrinho."""
    await state.set_state(ShopStates.in_cart)
    data = await state.get_data()
    cart = data.get("cart", [])
    
    if not cart:
        await callback.message.edit_text(
            "🛒 *Seu Carrinho*\n\nSeu carrinho está vazio.",
            parse_mode="Markdown",
            # reply_markup=get_cart_keyboard(has_items=False)
        )
    else:
        # Recuperaríamos do DB os detalhes usando os IDs em `cart`
        await callback.message.edit_text(
            f"🛒 *Seu Carrinho*\n\nVocê tem {len(cart)} item(ns).\n\n(Integração pendente)",
            parse_mode="Markdown",
            # reply_markup=get_cart_keyboard(has_items=True)
        )
    await callback.answer()


@cart_router.callback_query(F.data == "cart_clear")
async def clear_cart(callback: CallbackQuery, state: FSMContext):
    """Esvazia o carrinho."""
    await state.update_data(cart=[])
    await callback.message.edit_text("🗑️ Seu carrinho foi esvaziado.")
    await callback.answer("Carrinho vazio!")
