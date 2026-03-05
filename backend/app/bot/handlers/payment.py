# =============================================================================
# VimaBOT SaaS - Handler: Pagamento
# =============================================================================
# Fluxo de checkout, fechamento do pedido e instruções de pagamento PIX.
# =============================================================================

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

# from app.bot.keyboards import get_payment_keyboard
from app.bot.states import ShopStates

payment_router = Router(name="payment_router")


@payment_router.callback_query(F.data == "cart_checkout", ShopStates.in_cart)
async def process_checkout(callback: CallbackQuery, state: FSMContext, bot_tenant_id: str):
    """
    Inicia o checkout.
    Cria a Order no banco de dados com status 'pending' usando o tenant_id.
    Gera o payload pix manual (ou chama API OpenPix na fase 4).
    """
    data = await state.get_data()
    cart = data.get("cart", [])
    
    if not cart:
        await callback.answer("Seu carrinho está vazio!", show_alert=True)
        return
        
    await state.set_state(ShopStates.payment_pix)
    
    # Criar Order no DB
    # buscar infos de pagamento do tenant no config
    
    payment_instructions = (
        "💳 *Pagamento PIX*\n\n"
        "1. Copie a chave PIX abaixo.\n"
        "2. Faça a transferência no valor de R$ X,XX no app do seu banco.\n\n"
        "`chave_pix_exemplo`\n\n"
        "Após o pagamento, clique em *Enviar Comprovante*."
    )
    
    await callback.message.edit_text(
        payment_instructions,
        parse_mode="Markdown",
        # reply_markup=get_payment_keyboard(order_id="id_gerado")
    )
    await callback.answer()


@payment_router.callback_query(F.data.startswith("send_receipt:"), ShopStates.payment_pix)
async def prompt_for_receipt(callback: CallbackQuery, state: FSMContext):
    """Avisa o usuário que ele já pode enviar a imagem."""
    order_id = callback.data.split(":")[1]
    await state.update_data(current_order_id=order_id)
    
    await callback.message.answer(
        "📸 Por favor, envie a foto ou print do seu comprovante de pagamento agora."
    )
    await callback.answer()


@payment_router.message(F.photo | F.document, ShopStates.payment_pix)
async def handle_receipt_upload(message: Message, state: FSMContext, bot_tenant_id: str):
    """
    Recebe a foto, faz download em temporário, salva no Minio (Fase 4)
    e atualiza a Order para 'validation'.
    """
    data = await state.get_data()
    order_id = data.get("current_order_id")
    
    if not order_id:
        await message.answer("Erro: Não encontramos seu pedido atual. Volte ao menu principal.")
        await state.clear()
        return
        
    await message.answer("✅ Comprovante recebido! Seu pagamento está em fase de validação. Avisaremos assim que o pedido for liberado.")
    await state.clear()
    
    # TODO Na fase 4:
    # 1. Baixar imagem com `bot.download()`
    # 2. Upload Minio S3 com prefixo `tenant-{bot_tenant_id}/comprovantes/{order_id}`
    # 3. Atualizar BD `orders` para status `validation` e `comprovante_s3_key`
