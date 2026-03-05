# =============================================================================
# VimaBOT SaaS - Schemas de Produto
# =============================================================================
# Schemas Pydantic para CRUD de produtos digitais de cada tenant.
# =============================================================================

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# =============================================================================
# Schema Base (campos compartilhados)
# =============================================================================
class ProductBase(BaseModel):
    """Campos compartilhados entre criação e resposta de produtos."""
    name: str = Field(
        ...,
        min_length=2,
        max_length=300,
        description="Nome do produto exibido no catálogo do bot",
        examples=["Filme Ação 2026 - Full HD"],
    )
    description: Optional[str] = Field(
        default=None,
        description="Descrição detalhada do produto",
        examples=["Filme de ação completo em alta definição"],
    )
    price: float = Field(
        ...,
        gt=0,
        le=99999999.99,
        description="Preço do produto em R$ (Reais)",
        examples=[29.90],
    )


# =============================================================================
# Schema de Criação (POST)
# =============================================================================
class ProductCreate(ProductBase):
    """
    Schema para criação de um novo produto.

    O s3_key é preenchido automaticamente após o upload do arquivo
    para o Minio S3. O padrão é: tenant-{id}/products/{nome_arquivo}
    """
    s3_key: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Caminho do arquivo no bucket S3 do tenant",
        examples=["tenant-abc123/products/filme_2026.mp4"],
    )
    is_active: bool = Field(
        default=True,
        description="Se o produto está visível no catálogo",
    )


# =============================================================================
# Schema de Atualização (PUT/PATCH)
# =============================================================================
class ProductUpdate(BaseModel):
    """
    Schema para atualização parcial de um produto.

    Todos os campos são opcionais. Permite desativar um produto
    sem removê-lo do banco (toggle is_active).
    """
    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=300,
        description="Novo nome do produto",
    )
    description: Optional[str] = Field(
        default=None,
        description="Nova descrição do produto",
    )
    price: Optional[float] = Field(
        default=None,
        gt=0,
        le=99999999.99,
        description="Novo preço em R$",
    )
    s3_key: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=500,
        description="Novo caminho do arquivo no S3",
    )
    is_active: Optional[bool] = Field(
        default=None,
        description="Ativar/desativar o produto no catálogo",
    )


# =============================================================================
# Schema de Resposta (GET)
# =============================================================================
class ProductResponse(ProductBase):
    """Schema de resposta com dados completos do produto."""
    id: uuid.UUID = Field(..., description="ID único do produto")
    tenant_id: uuid.UUID = Field(..., description="ID do tenant proprietário")
    s3_key: str = Field(..., description="Caminho do arquivo no S3")
    is_active: bool = Field(..., description="Se está visível no catálogo")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")

    model_config = {"from_attributes": True}


# =============================================================================
# Schema de Lista (GET /products)
# =============================================================================
class ProductListResponse(BaseModel):
    """Schema de resposta para listagem de produtos do tenant."""
    products: list[ProductResponse] = Field(..., description="Lista de produtos")
    total: int = Field(..., description="Total de registros")
