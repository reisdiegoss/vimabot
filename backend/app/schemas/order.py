# =============================================================================
# VimaBOT SaaS - Schemas de Pedido (Order)
# =============================================================================
# Schemas Pydantic para gestão de pedidos e Kanban do tenant.
# =============================================================================

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models import OrderStatus


# =============================================================================
# Schema de Criação (POST) - Usado pelo Bot Engine
# =============================================================================
class OrderCreate(BaseModel):
    """
    Schema para criação de um novo pedido.

    Criado automaticamente pelo Bot Engine quando um comprador
    seleciona um produto no Telegram.
    """
    product_id: uuid.UUID = Field(
        ...,
        description="ID do produto selecionado pelo comprador",
    )
    customer_telegram_id: int = Field(
        ...,
        description="ID do Telegram do comprador",
    )
    customer_name: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Nome do comprador no Telegram",
    )
    gateway: str = Field(
        ...,
        description="Gateway de pagamento: 'vimapix' ou 'openpix'",
        examples=["vimapix"],
    )


# =============================================================================
# Schema de Atualização de Status (PATCH) - Kanban
# =============================================================================
class OrderStatusUpdate(BaseModel):
    """
    Schema para atualização de status de um pedido no Kanban.

    O tenant usa este schema para mover cards entre colunas:
        pending → validation → paid → delivered
    """
    status: OrderStatus = Field(
        ...,
        description="Novo status do pedido no fluxo Kanban",
    )


# =============================================================================
# Schema de Atualização de Comprovante (PATCH) - Vimapix
# =============================================================================
class OrderComprovanteUpdate(BaseModel):
    """
    Schema para registrar o comprovante de pagamento enviado pelo comprador.

    Usado pelo Bot Engine quando o comprador envia a foto do comprovante.
    O arquivo é salvo no Minio S3 e o caminho registrado aqui.
    """
    comprovante_s3_key: str = Field(
        ...,
        max_length=500,
        description="Caminho do comprovante no bucket S3",
    )
    txid: Optional[str] = Field(
        default=None,
        max_length=100,
        description="ID da transação PIX",
    )


# =============================================================================
# Schema de Resposta (GET)
# =============================================================================
class OrderResponse(BaseModel):
    """Schema de resposta com dados completos do pedido."""
    id: uuid.UUID = Field(..., description="ID único do pedido")
    tenant_id: uuid.UUID = Field(..., description="ID do tenant vendedor")
    product_id: Optional[uuid.UUID] = Field(None, description="ID do produto")
    customer_telegram_id: int = Field(..., description="ID Telegram do comprador")
    customer_name: Optional[str] = Field(None, description="Nome do comprador")
    total_amount: float = Field(..., description="Valor total em R$")
    status: OrderStatus = Field(..., description="Status atual no Kanban")
    gateway: Optional[str] = Field(None, description="Gateway de pagamento")
    txid: Optional[str] = Field(None, description="ID da transação PIX")
    comprovante_s3_key: Optional[str] = Field(None, description="Caminho do comprovante no S3")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")

    # Dados do produto (para exibição no Kanban sem query extra)
    product_name: Optional[str] = Field(None, description="Nome do produto comprado")

    model_config = {"from_attributes": True}


# =============================================================================
# Schema de Lista Kanban (GET /orders)
# =============================================================================
class OrderListResponse(BaseModel):
    """Schema de resposta para listagem de pedidos (Kanban)."""
    orders: list[OrderResponse] = Field(..., description="Lista de pedidos")
    total: int = Field(..., description="Total de registros")


# =============================================================================
# Schema de Contadores por Status (GET /orders/stats)
# =============================================================================
class OrderStatsResponse(BaseModel):
    """
    Contadores de pedidos agrupados por status.

    Usado no cabeçalho do Kanban para exibir a quantidade de cards
    em cada coluna sem precisar carregar todos os dados.
    """
    pending: int = Field(default=0, description="Aguardando pagamento")
    validation: int = Field(default=0, description="Validação de comprovante")
    paid: int = Field(default=0, description="Pagos (processando entrega)")
    delivered: int = Field(default=0, description="Finalizados (entregues)")
    total: int = Field(default=0, description="Total de pedidos")
