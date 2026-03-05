# =============================================================================
# VimaBOT SaaS - Router de Webhooks
# =============================================================================
# Recebe os callbacks de transações concluídas no meio de pagamento (OpenPix).
# Faz a atualização do status da Order.
#
# Segurança: Como os Webhooks são chamados por terceiros, usa-se Webhook HMAC 
# Signature ou verificação de Header para validar o originador.
# =============================================================================

from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Order, OrderStatus
# No futuro, incluir validação de HMAC Signature via OpenPix lib ou custom
# from openpix... import verify_signature

router = APIRouter(
    prefix="/api/v1/webhooks",
    tags=["Integrações / Webhooks"],
)


@router.post("/openpix", summary="Webhook do OpenPix")
async def openpix_webhook(
    request: Request,
    payload: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """
    Recebe a confirmação de que um PIX OpenPix foi pago com sucesso.
    
    Espera na payload algo como:
    {
      "event": "CHARGE_COMPLETED",
      "charge": {
         "correlationID": "uuid-da-order",
         "status": "COMPLETED",
         "value": 15000 ...
      }
    }
    """
    # 1. (Opcional) Validar X-Webhook-Signature nos Headers
    # signature = request.headers.get("x-webhook-signature")
    
    event_type = payload.get("event")
    
    # Se for estorno/expiração a lógica muda. Vamos tratar pagamento ok:
    if event_type != "CHARGE_COMPLETED":
        return {"status": "ignored", "reason": f"unhandled event_type {event_type}"}

    charge_data = payload.get("charge", {})
    correlation_id = charge_data.get("correlationID")
    
    if not correlation_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Falta correlationID."
        )

    # 2. Buscar a ordem
    result = await db.execute(
        select(Order).where(Order.id == correlation_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order não encontrada."
        )

    # 3. Atualiza estado para PAID ou DELIVERED e processa a entrega automágica.
    # Pode enviar mensagem pelo bot informando o usuario! (Futuro usando BotManager)
    
    if order.status != OrderStatus.PAID and order.status != OrderStatus.DELIVERED:
        order.status = OrderStatus.PAID
        await db.commit()
        
    return {"status": "ok", "message": "Webhook processado."}
