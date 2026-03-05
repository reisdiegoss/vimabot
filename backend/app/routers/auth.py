# =============================================================================
# VimaBOT SaaS - Router de Autenticação
# =============================================================================
# Rotas de login e autenticação da plataforma.
#
# Endpoints:
#   POST /api/v1/auth/login  → Autenticação com email e senha, retorna JWT.
#   GET  /api/v1/auth/me     → Retorna dados do tenant autenticado.
# =============================================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Tenant
from app.security import verify_password, create_access_token
from app.dependencies import get_current_tenant
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.tenant import TenantResponse

# Instância do router de autenticação
router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Autenticação"],
)


# =============================================================================
# POST /api/v1/auth/login - Login na Plataforma
# =============================================================================
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login na plataforma",
    description=(
        "Autentica um tenant ou Super-Admin com email e senha. "
        "Retorna um token JWT para uso nas rotas protegidas."
    ),
)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Autentica o usuário e retorna um token JWT.

    Fluxo:
        1. Busca o tenant pelo email no banco de dados.
        2. Verifica se o tenant existe.
        3. Verifica se a senha está correta (bcrypt).
        4. Verifica se a conta está ativa.
        5. Gera e retorna o token JWT com claims do tenant.

    Args:
        request: Email e senha do tenant (validados pelo Pydantic).
        db: Sessão do banco de dados (injetada automaticamente).

    Returns:
        TokenResponse com access_token e dados do tenant.

    Raises:
        HTTPException 401: Email ou senha incorretos.
        HTTPException 403: Conta suspensa ou inativa.
    """
    # 1. Busca o tenant pelo email
    result = await db.execute(
        select(Tenant).where(Tenant.owner_email == request.email)
    )
    tenant = result.scalar_one_or_none()

    # 2. Verifica se o tenant existe
    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Verifica a senha com bcrypt
    if not verify_password(request.password, tenant.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4. Verifica se a conta está ativa
    if tenant.status.value == "suspended":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta suspensa. Entre em contato com o suporte.",
        )

    if tenant.status.value == "inactive":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta inativa. Reative sua conta para continuar.",
        )

    # 5. Gera o token JWT com os claims do tenant
    access_token = create_access_token(
        tenant_id=str(tenant.id),
        email=tenant.owner_email,
        is_superadmin=tenant.is_superadmin,
    )

    # 6. Retorna o token e dados básicos do tenant
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        tenant_id=str(tenant.id),
        email=tenant.owner_email,
        company_name=tenant.company_name,
        is_superadmin=tenant.is_superadmin,
    )


# =============================================================================
# GET /api/v1/auth/me - Dados do Tenant Autenticado
# =============================================================================
@router.get(
    "/me",
    response_model=TenantResponse,
    summary="Meus dados",
    description="Retorna os dados do tenant autenticado pelo token JWT.",
)
async def get_me(
    tenant: Tenant = Depends(get_current_tenant),
) -> TenantResponse:
    """
    Retorna os dados do tenant que está autenticado.

    Útil para o frontend carregar as informações do usuário logado
    após o login ou ao recarregar a página.

    Args:
        tenant: Tenant autenticado (injetado via dependência JWT).

    Returns:
        Dados completos do tenant (sem a senha).
    """
    return TenantResponse.model_validate(tenant)
