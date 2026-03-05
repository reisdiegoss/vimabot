# =============================================================================
# VimaBOT SaaS - Handler: Carrinho
# =============================================================================
# Gerencia o carrinho de compras salvo em memória no estado (FSM).
# =============================================================================

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Product
from app.bot.keyboards import get_cart_keyboard
from app.bot.states import ShopStates

cart_router = Router(name="cart_router")


@cart_router.callback_query(F.data.startswith("add_cart:"))
async def add_to_cart(callback: CallbackQuery, state: FSMContext, bot_tenant_id: str, db: AsyncSession):
    """Adiciona um produto ao carrinho (salvo no FSMContext)."""
    product_id = callback.data.split(":")[1]
    
    # Verifica se produto existe
    result = await db.execute(select(Product).where(Product.id == product_id, Product.tenant_id == bot_tenant_id))
    product = result.scalar_one_or_none()
    if not product:
        await callback.answer("Produto indisponível.", show_alert=True)
        return
        
    data = await state.get_data()
    cart = data.get("cart", [])
    
    # Adicionar o ID e o Valor
    cart.append({"id": str(product.id), "name": product.name, "price": float(product.price)})
    
    await state.update_data(cart=cart)
    await callback.answer(f"✅ {product.name} adicionado!", show_alert=True)
    
    
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
            reply_markup=get_cart_keyboard(has_items=False)
        )
    else:
        total = sum(item["price"] for item in cart)
        items_str = "\n".join([f"- {item['name']} (R$ {item['price']:.2f})" for item in cart])
        await callback.message.edit_text(
            f"🛒 *Seu Carrinho*\n\n{items_str}\n\n*Total: R$ {total:.2f}*",
            parse_mode="Markdown",
            reply_markup=get_cart_keyboard(has_items=True)
        )
    await callback.answer()


@cart_router.callback_query(F.data == "cart_clear")
async def clear_cart(callback: CallbackQuery, state: FSMContext):
    """Esvazia o carrinho."""
    await state.update_data(cart=[])
    await callback.message.edit_text(
        "🗑️ Seu carrinho foi esvaziado.", 
        reply_markup=get_cart_keyboard(has_items=False)
    )
    await callback.answer("Carrinho vazio!")
