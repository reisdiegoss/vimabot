# =============================================================================
# VimaBOT SaaS - Router de Pedidos (Orders / Kanban)
# =============================================================================
# Gestão de pedidos do tenant com suporte ao fluxo Kanban.
# Cada tenant só vê seus próprios pedidos.
# =============================================================================

import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models import Tenant, Product, Order, OrderStatus
from app.dependencies import get_current_tenant
from app.schemas.order import (
    OrderCreate,
    OrderStatusUpdate,
    OrderComprovanteUpdate,
    OrderResponse,
    OrderListResponse,
    OrderStatsResponse,
)

router = APIRouter(
    prefix="/api/v1/orders",
    tags=["Pedidos (Kanban)"],
)


def _order_to_response(order: Order) -> OrderResponse:
    """Converte um Order ORM para OrderResponse incluindo product_name."""
    product_name = None
    if order.product is not None:
        product_name = order.product.name

    return OrderResponse(
        id=order.id,
        tenant_id=order.tenant_id,
        product_id=order.product_id,
        customer_telegram_id=order.customer_telegram_id,
        customer_name=order.customer_name,
        total_amount=float(order.total_amount),
        status=order.status,
        gateway=order.gateway,
        txid=order.txid,
        comprovante_s3_key=order.comprovante_s3_key,
        created_at=order.created_at,
        updated_at=order.updated_at,
        product_name=product_name,
    )


@router.get(
    "/stats",
    response_model=OrderStatsResponse,
    summary="Contadores Kanban",
)
async def get_order_stats(
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
) -> OrderStatsResponse:
    """Retorna contadores de pedidos agrupados por status para o Kanban."""
    result = await db.execute(
        select(Order.status, func.count(Order.id))
        .where(Order.tenant_id == tenant.id)
        .group_by(Order.status)
    )
    counts = {row[0].value: row[1] for row in result.all()}

    pending = counts.get("pending", 0)
    validation = counts.get("validation", 0)
    paid = counts.get("paid", 0)
    delivered = counts.get("delivered", 0)

    return OrderStatsResponse(
        pending=pending,
        validation=validation,
        paid=paid,
        delivered=delivered,
        total=pending + validation + paid + delivered,
    )


@router.get(
    "",
    response_model=OrderListResponse,
    summary="Listar pedidos",
)
async def list_orders(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    status_filter: OrderStatus | None = Query(default=None, alias="status"),
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
) -> OrderListResponse:
    """Lista pedidos do tenant com filtro opcional por status (coluna Kanban)."""
    base_query = select(Order).where(Order.tenant_id == tenant.id)
    count_query = select(func.count(Order.id)).where(Order.tenant_id == tenant.id)

    if status_filter is not None:
        base_query = base_query.where(Order.status == status_filter)
        count_query = count_query.where(Order.status == status_filter)

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    result = await db.execute(
        base_query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
    )
    orders = result.scalars().all()

    return OrderListResponse(
        orders=[_order_to_response(o) for o in orders],
        total=total,
    )


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Detalhes do pedido",
)
async def get_order(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
) -> OrderResponse:
    """Retorna os dados completos de um pedido do tenant."""
    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.tenant_id == tenant.id,
        )
    )
    order = result.scalar_one_or_none()

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido não encontrado.",
        )

    return _order_to_response(order)


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar pedido",
)
async def create_order(
    data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
) -> OrderResponse:
    """
    Cria um novo pedido. Chamado pelo Bot Engine quando o comprador
    seleciona um produto no Telegram.
    """
    # Busca o produto para obter o preço
    product_result = await db.execute(
        select(Product).where(
            Product.id == data.product_id,
            Product.tenant_id == tenant.id,
            Product.is_active == True,  # noqa: E712
        )
    )
    product = product_result.scalar_one_or_none()

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado ou inativo.",
        )

    # Gera o txid baseado no ID do pedido
    import secrets
    txid = secrets.token_hex(16)

    new_order = Order(
        tenant_id=tenant.id,
        product_id=product.id,
        customer_telegram_id=data.customer_telegram_id,
        customer_name=data.customer_name,
        total_amount=product.price,
        status=OrderStatus.PENDING,
        gateway=data.gateway,
        txid=txid,
    )
    db.add(new_order)
    await db.flush()

    # Recarrega com relationship do product para product_name
    await db.refresh(new_order, ["product"])

    return _order_to_response(new_order)


@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
    summary="Atualizar status (Kanban)",
)
async def update_order_status(
    order_id: uuid.UUID,
    data: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
) -> OrderResponse:
    """Atualiza o status de um pedido (mover card no Kanban)."""
    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.tenant_id == tenant.id,
        )
    )
    order = result.scalar_one_or_none()

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido não encontrado.",
        )

    order.status = data.status
    return _order_to_response(order)


@router.patch(
    "/{order_id}/comprovante",
    response_model=OrderResponse,
    summary="Registrar comprovante",
)
async def update_order_comprovante(
    order_id: uuid.UUID,
    data: OrderComprovanteUpdate,
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
) -> OrderResponse:
    """
    Registra o comprovante de pagamento enviado pelo comprador.
    Move o pedido para status 'validation' no Kanban.
    """
    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.tenant_id == tenant.id,
        )
    )
    order = result.scalar_one_or_none()

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido não encontrado.",
        )

    order.comprovante_s3_key = data.comprovante_s3_key
    if data.txid:
        order.txid = data.txid
    order.status = OrderStatus.VALIDATION

    return _order_to_response(order)
