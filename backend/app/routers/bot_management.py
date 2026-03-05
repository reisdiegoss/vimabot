# =============================================================================
# VimaBOT SaaS - Router de Gestão do Bot
# =============================================================================
# Permite ao tenant iniciar e parar a instância do seu bot no servidor.
# =============================================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Tenant, BotConfig
from app.dependencies import get_current_tenant
from app.bot.manager import bot_manager

router = APIRouter(
    prefix="/api/v1/bot",
    tags=["Gestão do Bot"],
)


@router.post("/start", summary="Iniciar bot no servidor")
async def start_bot_instance(
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    """
    Inicia o long-polling do aiogram para o bot do tenant autenticado.
    Verifica se o token foi configurado antes.
    """
    result = await db.execute(
        select(BotConfig).where(BotConfig.tenant_id == tenant.id)
    )
    config = result.scalar_one_or_none()

    if not config or not config.bot_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token do bot não configurado.",
        )

    t_id_str = str(tenant.id)
    
    if bot_manager.is_running(t_id_str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O bot já está em execução.",
        )

    success = await bot_manager.start_bot(t_id_str, config.bot_token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Falha ao iniciar o bot. Verifique se o token é válido.",
        )
        
    config.is_running = True
    await db.commit()

    return {"status": "ok", "message": "Bot iniciado com sucesso."}


@router.post("/stop", summary="Parar bot no servidor")
async def stop_bot_instance(
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    """
    Para a instância do bot (desliga o long-polling localmente).
    """
    result = await db.execute(
        select(BotConfig).where(BotConfig.tenant_id == tenant.id)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuração não encontrada.",
        )

    t_id_str = str(tenant.id)
    
    if not bot_manager.is_running(t_id_str):
        if config.is_running:
            config.is_running = False
            await db.commit()
            
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O bot não está em execução no momento.",
        )

    success = await bot_manager.stop_bot(t_id_str)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Falha ao parar o bot.",
        )
        
    config.is_running = False
    await db.commit()

    return {"status": "ok", "message": "Bot parado com sucesso."}
