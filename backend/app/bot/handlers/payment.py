# =============================================================================
# VimaBOT SaaS - Handler: Pagamento
# =============================================================================
# Fluxo de checkout, fechamento do pedido e instruções de pagamento PIX.
# Usa os serviços StorageService para s3 e PixService.
# =============================================================================

import io
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Order, BotConfig, OrderStatus, Product
from app.bot.keyboards import get_payment_keyboard
from app.bot.states import ShopStates
from app.services.pix import PixService
from app.services.storage import StorageService
from app.config import settings

payment_router = Router(name="payment_router")


@payment_router.callback_query(F.data == "cart_checkout", ShopStates.in_cart)
async def process_checkout(callback: CallbackQuery, state: FSMContext, bot_tenant_id: str, db: AsyncSession):
    """
    Inicia o checkout.
    Cria a Order no banco de dados com status 'pending' usando o tenant_id.
    Gera o payload pix manual usando a chave do Tenant.
    """
    data = await state.get_data()
    cart = data.get("cart", [])
    
    if not cart:
        await callback.answer("Seu carrinho está vazio!", show_alert=True)
        return
        
    # Pega config do tenant
    config_result = await db.execute(select(BotConfig).where(BotConfig.tenant_id == bot_tenant_id))
    bot_config = config_result.scalar_one_or_none()
    
    if not bot_config or not bot_config.vimapix_key:
        await callback.answer("Opção de pagamento indisponível no momento. Tente novamente mais tarde.", show_alert=True)
        return

    await state.set_state(ShopStates.payment_pix)
    
    # Para simplicidade da v1, e porque só permitimos comprar um produto por vez no pix direto (ou a soma total),
    # Vamos pegar o valor total e o ID do primeiro produto (MVP focando no produto principal/único adicionado)
    # Numa versão avançada poderíamos criar tabela order_items
    total_amount = sum(item["price"] for item in cart)
    product_id = cart[0]["id"]
    
    # Criar Order no DB
    new_order = Order(
        tenant_id=bot_tenant_id,
        customer_telegram_id=str(callback.from_user.id),
        customer_name=callback.from_user.full_name or "Desconhecido",
        product_id=product_id,
        total_amount=total_amount,
        status=OrderStatus.PENDING,
        gateway="Manual/Vimapix"
    )
    db.add(new_order)
    await db.commit() # Salva gerar ID
    await db.refresh(new_order)
    
    # Gera código Pix
    pix_payload = await PixService.generate_manual_pix(
        tenant_config=bot_config,
        order_id=new_order.id,
        total_amount=total_amount
    )
    
    if not pix_payload:
        await callback.answer("Erro ao gerar fatura PIX. Fale com o dono da loja.", show_alert=True)
        return
    
    payment_instructions = (
        "💳 *Pagamento PIX*\n\n"
        "1. Copie a chave PIX abaixo.\n"
        f"2. Faça a transferência no valor de *R$ {total_amount:.2f}* no app do seu banco.\n\n"
        f"`{pix_payload}`\n\n"
        "Após o pagamento, clique em *Enviar Comprovante*."
    )
    
    await callback.message.edit_text(
        payment_instructions,
        parse_mode="Markdown",
        reply_markup=get_payment_keyboard(order_id=str(new_order.id))
    )
    await callback.answer()


@payment_router.callback_query(F.data.startswith("send_receipt:"), ShopStates.payment_pix)
async def prompt_for_receipt(callback: CallbackQuery, state: FSMContext):
    """Avisa o usuário que ele já pode enviar a imagem."""
    order_id = callback.data.split(":")[1]
    await state.update_data(current_order_id=order_id)
    
    await callback.message.answer(
        "📸 Por favor, envie a foto ou documento (PDF/Imagem) do seu comprovante de pagamento agora."
    )
    await callback.answer()


@payment_router.message(F.photo | F.document, ShopStates.payment_pix)
async def handle_receipt_upload(message: Message, state: FSMContext, bot_tenant_id: str, db: AsyncSession):
    """
    Recebe a foto, baixa para memória e salva no Minio (S3).
    A Order vai para status de Validation.
    """
    data = await state.get_data()
    order_id = data.get("current_order_id")
    
    if not order_id:
        await message.answer("Erro: Não encontramos seu pedido atual. Volte ao menu principal com /start.")
        await state.clear()
        return
        
    order_result = await db.execute(select(Order).where(Order.id == order_id, Order.tenant_id == bot_tenant_id))
    order = order_result.scalar_one_or_none()
    
    if not order:
        await message.answer("Pedido não encontrado.")
        await state.clear()
        return
        
    config_result = await db.execute(select(BotConfig).where(BotConfig.tenant_id == bot_tenant_id))
    bot_config = config_result.scalar_one()

    # Prepara o bot para download em memória
    file_id = message.photo[-1].file_id if message.photo else message.document.file_id
    file = await message.bot.get_file(file_id)
    
    # Download memory (BytesIO)
    file_bytes_io = io.BytesIO()
    await message.bot.download_file(file.file_path, destination=file_bytes_io)
    file_bytes = file_bytes_io.getvalue()
    
    # S3 Upload
    storage = StorageService(
        endpoint_url=bot_config.minio_endpoint or settings.minio_endpoint,
        access_key=bot_config.minio_access_key or settings.minio_access_key,
        secret_key=bot_config.minio_secret_key or settings.minio_secret_key,
        bucket_name=bot_config.minio_bucket or settings.minio_bucket,
        use_ssl=bot_config.minio_use_ssl if bot_config.minio_use_ssl is not None else settings.minio_use_ssl
    )
    
    # Ex: tenant-88ad3f.../comprovantes/order-88ad3f...jpg
    extension = ".jpg" if message.photo else ".pdf" # Simplificação
    object_name = f"tenant-{bot_tenant_id}/comprovantes/order-{order_id}{extension}"
    
    success = await storage.upload_file(file_bytes, object_name)
    
    if success:
        order.comprovante_s3_key = object_name
        order.status = OrderStatus.VALIDATION
        await db.commit()
        await message.answer("✅ Comprovante recebido com sucesso!\n\nSeu pagamento está em fase de validação. Avisaremos assim que o pedido for liberado.")
        await state.clear()
    else:
        await message.answer("❌ Houve um erro ao enviar o comprovante para o nosso serviço de armazamento de forma segura. Tente novamente agorinha.")
