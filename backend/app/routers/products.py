# =============================================================================
# VimaBOT SaaS - Router de Produtos
# =============================================================================
# CRUD de produtos digitais. Cada tenant gerencia seu próprio catálogo.
# O tenant autenticado só vê e manipula seus próprios produtos.
# =============================================================================

import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models import Tenant, Product
from app.dependencies import get_current_tenant
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
)

router = APIRouter(
    prefix="/api/v1/products",
    tags=["Produtos"],
)


@router.get(
    "",
    response_model=ProductListResponse,
    summary="Listar produtos do tenant",
)
async def list_products(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    active_only: bool = Query(default=False, description="Filtrar apenas ativos"),
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
) -> ProductListResponse:
    """Lista os produtos do tenant autenticado com paginação."""
    # Query base filtrada pelo tenant_id do usuário logado
    base_query = select(Product).where(Product.tenant_id == tenant.id)
    count_query = select(func.count(Product.id)).where(Product.tenant_id == tenant.id)

    # Filtro opcional: apenas produtos ativos
    if active_only:
        base_query = base_query.where(Product.is_active == True)  # noqa: E712
        count_query = count_query.where(Product.is_active == True)  # noqa: E712

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    result = await db.execute(
        base_query.order_by(Product.created_at.desc()).offset(skip).limit(limit)
    )
    products = result.scalars().all()

    return ProductListResponse(
        products=[ProductResponse.model_validate(p) for p in products],
        total=total,
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Detalhes de um produto",
)
async def get_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
) -> ProductResponse:
    """Retorna os dados de um produto do tenant autenticado."""
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.tenant_id == tenant.id,
        )
    )
    product = result.scalar_one_or_none()

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )

    return ProductResponse.model_validate(product)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar produto",
)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
) -> ProductResponse:
    """Cria um novo produto no catálogo do tenant autenticado."""
    new_product = Product(
        tenant_id=tenant.id,
        name=data.name,
        description=data.description,
        s3_key=data.s3_key,
        price=data.price,
        is_active=data.is_active,
    )
    db.add(new_product)
    await db.flush()

    return ProductResponse.model_validate(new_product)


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Atualizar produto",
)
async def update_product(
    product_id: uuid.UUID,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
) -> ProductResponse:
    """Atualiza parcialmente um produto do tenant autenticado."""
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.tenant_id == tenant.id,
        )
    )
    product = result.scalar_one_or_none()

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    return ProductResponse.model_validate(product)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover produto",
)
async def delete_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
) -> None:
    """Remove permanentemente um produto do tenant autenticado."""
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.tenant_id == tenant.id,
        )
    )
    product = result.scalar_one_or_none()

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )

    await db.delete(product)
