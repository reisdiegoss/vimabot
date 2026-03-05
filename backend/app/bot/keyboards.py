# =============================================================================
# VimaBOT SaaS - Teclados (Keyboards) do Bot
# =============================================================================

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_menu() -> InlineKeyboardMarkup:
    """Menu principal do bot."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🛍️ Catálogo", callback_data="shop_catalog"),
        InlineKeyboardButton(text="🛒 Carrinho", callback_data="shop_cart")
    )
    builder.row(
        InlineKeyboardButton(text="📦 Meus Pedidos", callback_data="shop_orders")
    )
    return builder.as_markup()

def get_catalog_keyboard(products: list, page: int = 1, total_pages: int = 1) -> InlineKeyboardMarkup:
    """Teclado inline com a lista de produtos."""
    builder = InlineKeyboardBuilder()
    
    for product in products:
        # callback_data armazenará o action e o ID do produto
        # ex: "add_cart:<id_do_produto>"
        # Como o ID do produto é UUID (36 chars) e o limite é 64, cabe perfeitamente.
        builder.row(
            InlineKeyboardButton(
                text=f"{product.name} - R$ {product.price:.2f}",
                callback_data=f"prod_info:{product.id}"
            )
        )
    
    # Navegação de páginas
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Ant.", callback_data=f"cat_page:{page-1}"))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="Próx. ➡️", callback_data=f"cat_page:{page+1}"))
    
    if nav_buttons:
        builder.row(*nav_buttons)
        
    builder.row(InlineKeyboardButton(text="🔙 Voltar", callback_data="main_menu"))
    return builder.as_markup()

def get_product_details_keyboard(product_id: str) -> InlineKeyboardMarkup:
    """Teclado para a página de detalhes de um produto."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="➕ Adicionar ao Carrinho", callback_data=f"add_cart:{product_id}")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Voltar ao Catálogo", callback_data="shop_catalog")
    )
    return builder.as_markup()

def get_cart_keyboard(has_items: bool) -> InlineKeyboardMarkup:
    """Teclado do carrinho de compras."""
    builder = InlineKeyboardBuilder()
    if has_items:
        builder.row(
            InlineKeyboardButton(text="💳 Finalizar Compra", callback_data="cart_checkout"),
            InlineKeyboardButton(text="🗑️ Limpar Carrinho", callback_data="cart_clear")
        )
    builder.row(
        InlineKeyboardButton(text="🔙 Voltar", callback_data="main_menu")
    )
    return builder.as_markup()

def get_payment_keyboard(order_id: str) -> InlineKeyboardMarkup:
    """Teclado para tela de pagamento."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📸 Enviar Comprovante", callback_data=f"send_receipt:{order_id}")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Cancelar Pedido", callback_data=f"cancel_order:{order_id}")
    )
    return builder.as_markup()
