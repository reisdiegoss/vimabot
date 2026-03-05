# =============================================================================
# VimaBOT SaaS - Router de Tenants (Gestão de Clientes)
# =============================================================================
# CRUD completo de tenants. Acesso exclusivo do Super-Admin.
#
# Endpoints:
#   GET    /api/v1/tenants          → Listar todos os tenants
#   GET    /api/v1/tenants/{id}     → Detalhes de um tenant
#   POST   /api/v1/tenants          → Criar novo tenant (onboarding)
#   PUT    /api/v1/tenants/{id}     → Atualizar tenant
#   DELETE /api/v1/tenants/{id}     → Remover tenant
# =============================================================================

import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models import Tenant, BotConfig
from app.security import hash_password
from app.dependencies import require_superadmin
from app.schemas.tenant import (
    TenantCreate,
    TenantUpdate,
    TenantResponse,
    TenantListResponse,
)

# Instância do router de tenants (requer Super-Admin)
router = APIRouter(
    prefix="/api/v1/tenants",
    tags=["Tenants (Super-Admin)"],
)


# =============================================================================
# GET /api/v1/tenants - Listar Todos os Tenants
# =============================================================================
@router.get(
    "",
    response_model=TenantListResponse,
    summary="Listar tenants",
    description="Lista todos os tenants da plataforma. Acesso exclusivo do Super-Admin.",
)
async def list_tenants(
    skip: int = Query(default=0, ge=0, description="Registros para pular (paginação)"),
    limit: int = Query(default=50, ge=1, le=100, description="Máximo por página"),
    db: AsyncSession = Depends(get_db),
    _admin: Tenant = Depends(require_superadmin),
) -> TenantListResponse:
    """
    Lista todos os tenants cadastrados na plataforma.

    Suporta paginação via skip/limit. Ordenado por data de criação
    (mais recentes primeiro). Exclui o próprio Super-Admin da lista.

    Args:
        skip: Quantidade de registros para pular (offset).
        limit: Quantidade máxima de registros por página.
        db: Sessão do banco de dados.
        _admin: Verifica se é Super-Admin (dependência de autorização).

    Returns:
        Lista paginada de tenants com total de registros.
    """
    # Conta o total de tenants (excluindo Super-Admin)
    total_result = await db.execute(
        select(func.count(Tenant.id)).where(Tenant.is_superadmin == False)  # noqa: E712
    )
    total = total_result.scalar_one()

    # Busca os tenants com paginação
    result = await db.execute(
        select(Tenant)
        .where(Tenant.is_superadmin == False)  # noqa: E712
        .order_by(Tenant.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    tenants = result.scalars().all()

    return TenantListResponse(
        tenants=[TenantResponse.model_validate(t) for t in tenants],
        total=total,
    )


# =============================================================================
# GET /api/v1/tenants/{tenant_id} - Detalhes de um Tenant
# =============================================================================
@router.get(
    "/{tenant_id}",
    response_model=TenantResponse,
    summary="Detalhes do tenant",
    description="Retorna os dados de um tenant específico.",
)
async def get_tenant(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: Tenant = Depends(require_superadmin),
) -> TenantResponse:
    """
    Retorna os dados completos de um tenant específico.

    Args:
        tenant_id: UUID do tenant a ser consultado.
        db: Sessão do banco de dados.
        _admin: Verifica se é Super-Admin.

    Returns:
        Dados completos do tenant.

    Raises:
        HTTPException 404: Tenant não encontrado.
    """
    result = await db.execute(
        select(Tenant).where(Tenant.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()

    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant não encontrado.",
        )

    return TenantResponse.model_validate(tenant)


# =============================================================================
# POST /api/v1/tenants - Criar Novo Tenant (Onboarding)
# =============================================================================
@router.post(
    "",
    response_model=TenantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar tenant",
    description="Cria um novo tenant (onboarding de cliente).",
)
async def create_tenant(
    data: TenantCreate,
    db: AsyncSession = Depends(get_db),
    _admin: Tenant = Depends(require_superadmin),
) -> TenantResponse:
    """
    Cria um novo tenant na plataforma (onboarding).

    Fluxo:
        1. Verifica se o email já está em uso.
        2. Cria o registro do tenant com senha hasheada.
        3. Cria o registro de bot_config vazio (para configuração posterior).
        4. Retorna os dados do novo tenant.

    Args:
        data: Dados do novo tenant (nome, email, senha, plano).
        db: Sessão do banco de dados.
        _admin: Verifica se é Super-Admin.

    Returns:
        Dados do tenant recém-criado.

    Raises:
        HTTPException 409: Email já está em uso.
    """
    # 1. Verifica se o email já existe
    existing = await db.execute(
        select(Tenant).where(Tenant.owner_email == data.owner_email)
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este email já está em uso por outro tenant.",
        )

    # 2. Cria o tenant com senha hasheada (bcrypt)
    new_tenant = Tenant(
        company_name=data.company_name,
        owner_email=data.owner_email,
        password_hash=hash_password(data.password),
        plan_type=data.plan_type,
        subscription_due_date=data.subscription_due_date,
        is_superadmin=False,  # Nunca criar outro Super-Admin via API
    )
    db.add(new_tenant)
    # Flush para obter o ID gerado antes de criar o bot_config
    await db.flush()

    # 3. Cria o registro de bot_config vazio
    # O tenant preencherá as credenciais depois no painel
    bot_config = BotConfig(
        tenant_id=new_tenant.id,
        is_running=False,
    )
    db.add(bot_config)

    # O commit é feito automaticamente pelo get_db()
    return TenantResponse.model_validate(new_tenant)


# =============================================================================
# PUT /api/v1/tenants/{tenant_id} - Atualizar Tenant
# =============================================================================
@router.put(
    "/{tenant_id}",
    response_model=TenantResponse,
    summary="Atualizar tenant",
    description="Atualiza os dados de um tenant existente.",
)
async def update_tenant(
    tenant_id: uuid.UUID,
    data: TenantUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: Tenant = Depends(require_superadmin),
) -> TenantResponse:
    """
    Atualiza parcialmente os dados de um tenant.

    Apenas os campos fornecidos no body são atualizados.
    Permite alterar nome, email, plano, status e data de vencimento.
    Se uma nova senha for fornecida, será hasheada com bcrypt.

    Args:
        tenant_id: UUID do tenant a ser atualizado.
        data: Campos a serem atualizados (parcial).
        db: Sessão do banco de dados.
        _admin: Verifica se é Super-Admin.

    Returns:
        Dados atualizados do tenant.

    Raises:
        HTTPException 404: Tenant não encontrado.
        HTTPException 409: Novo email já está em uso.
    """
    # Busca o tenant no banco
    result = await db.execute(
        select(Tenant).where(Tenant.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()

    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant não encontrado.",
        )

    # Impede edição do Super-Admin via esta rota
    if tenant.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não é possível editar o Super-Admin por esta rota.",
        )

    # Atualiza apenas os campos fornecidos (exclude_unset ignora None)
    update_data = data.model_dump(exclude_unset=True)

    # Se o email foi alterado, verifica se já existe
    if "owner_email" in update_data:
        existing = await db.execute(
            select(Tenant).where(
                Tenant.owner_email == update_data["owner_email"],
                Tenant.id != tenant_id,
            )
        )
        if existing.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este email já está em uso.",
            )

    # Se a senha foi alterada, faz hash antes de salvar
    if "password" in update_data:
        update_data["password_hash"] = hash_password(update_data.pop("password"))

    # Aplica as atualizações no objeto ORM
    for field, value in update_data.items():
        setattr(tenant, field, value)

    return TenantResponse.model_validate(tenant)


# =============================================================================
# DELETE /api/v1/tenants/{tenant_id} - Remover Tenant
# =============================================================================
@router.delete(
    "/{tenant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover tenant",
    description="Remove permanentemente um tenant e todos os seus dados.",
)
async def delete_tenant(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: Tenant = Depends(require_superadmin),
) -> None:
    """
    Remove permanentemente um tenant da plataforma.

    ATENÇÃO: Esta operação é irreversível. Remove o tenant e todos os
    dados associados (bot_config, products, orders, managed_chats) via
    cascade delete definido nos modelos.

    Args:
        tenant_id: UUID do tenant a ser removido.
        db: Sessão do banco de dados.
        _admin: Verifica se é Super-Admin.

    Raises:
        HTTPException 404: Tenant não encontrado.
        HTTPException 403: Não é possível remover o Super-Admin.
    """
    result = await db.execute(
        select(Tenant).where(Tenant.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()

    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant não encontrado.",
        )

    if tenant.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não é possível remover o Super-Admin.",
        )

    # Para a instância do bot se ela estiver rodando no BotManager,
    # caso contrário teremos ghost bots gerando erros ao não achar o tenant
    from app.bot.manager import bot_manager
    if bot_manager.is_running(str(tenant_id)):
        await bot_manager.stop_bot(str(tenant_id))

    await db.delete(tenant)
