# =============================================================================
# VimaBOT SaaS - Router de Configuração do Bot
# =============================================================================
# Gerenciamento da configuração do bot Telegram de cada tenant.
# =============================================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Tenant, BotConfig
from app.dependencies import get_current_tenant
from app.schemas.bot_config import BotConfigUpdate, BotConfigResponse

router = APIRouter(
    prefix="/api/v1/bot-config",
    tags=["Configuração do Bot"],
)


def _mask_sensitive(value: str | None, visible_chars: int = 4) -> str | None:
    """Mascara um valor sensível exibindo apenas os últimos N caracteres."""
    if value is None or len(value) <= visible_chars:
        return value
    return "●" * 8 + value[-visible_chars:]


def _config_to_response(config: BotConfig) -> BotConfigResponse:
    """Converte BotConfig ORM para Response com campos sensíveis mascarados."""
    return BotConfigResponse(
        id=config.id,
        tenant_id=config.tenant_id,
        bot_token_masked=_mask_sensitive(config.bot_token),
        bot_username=config.bot_username,
        is_running=config.is_running,
        vimapix_key=config.vimapix_key,
        vimapix_beneficiary_name=config.vimapix_beneficiary_name,
        vimapix_beneficiary_city=config.vimapix_beneficiary_city,
        openpix_configured=config.openpix_apikey is not None,
        minio_endpoint=config.minio_endpoint,
        minio_bucket=config.minio_bucket,
        created_at=config.created_at,
        updated_at=config.updated_at,
    )


@router.get(
    "",
    response_model=BotConfigResponse,
    summary="Obter configuração do bot",
)
async def get_bot_config(
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
) -> BotConfigResponse:
    """Retorna a configuração do bot do tenant autenticado."""
    result = await db.execute(
        select(BotConfig).where(BotConfig.tenant_id == tenant.id)
    )
    config = result.scalar_one_or_none()

    if config is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuração do bot não encontrada.",
        )

    return _config_to_response(config)


@router.put(
    "",
    response_model=BotConfigResponse,
    summary="Atualizar configuração do bot",
)
async def update_bot_config(
    data: BotConfigUpdate,
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
) -> BotConfigResponse:
    """Atualiza a configuração do bot do tenant autenticado."""
    result = await db.execute(
        select(BotConfig).where(BotConfig.tenant_id == tenant.id)
    )
    config = result.scalar_one_or_none()

    if config is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuração do bot não encontrada.",
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)

    return _config_to_response(config)
