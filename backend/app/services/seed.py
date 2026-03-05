# =============================================================================
# VimaBOT SaaS - Seed do Super-Admin
# =============================================================================
# Cria o Super-Admin automaticamente na primeira execução da aplicação.
# Se o Super-Admin já existir, a função não faz nada.
# =============================================================================

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Tenant, BotConfig, PlanType, TenantStatus
from app.security import hash_password
from app.config import settings


async def seed_superadmin(db: AsyncSession) -> None:
    """
    Cria o registro do Super-Admin se ele ainda não existir.

    Usa as credenciais definidas nas variáveis de ambiente:
    - SUPERADMIN_EMAIL
    - SUPERADMIN_PASSWORD
    - SUPERADMIN_COMPANY
    """
    result = await db.execute(
        select(Tenant).where(Tenant.is_superadmin == True)  # noqa: E712
    )
    existing = result.scalar_one_or_none()

    if existing is not None:
        print(f"✅ Super-Admin já existe: {existing.owner_email}")
        return

    superadmin = Tenant(
        company_name=settings.superadmin_company,
        owner_email=settings.superadmin_email,
        password_hash=hash_password(settings.superadmin_password),
        plan_type=PlanType.ENTERPRISE,
        status=TenantStatus.ACTIVE,
        is_superadmin=True,
    )
    db.add(superadmin)
    await db.flush()

    bot_config = BotConfig(
        tenant_id=superadmin.id,
        is_running=False,
    )
    db.add(bot_config)

    await db.commit()
    print(f"🔑 Super-Admin criado: {settings.superadmin_email}")
