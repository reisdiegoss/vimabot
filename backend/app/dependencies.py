# =============================================================================
# VimaBOT SaaS - Dependências de Autenticação (FastAPI)
# =============================================================================
# Funções de dependência (Depends) para injeção automática nas rotas.
#
# Hierarquia de acesso:
#   - get_current_tenant: Qualquer usuário autenticado (Tenant ou Super-Admin).
#   - require_superadmin: Apenas o Super-Admin tem acesso.
#
# Uso nas rotas:
#   @router.get("/rota-protegida")
#   async def rota(tenant: Tenant = Depends(get_current_tenant)):
#       ...
#
#   @router.get("/rota-admin")
#   async def rota(tenant: Tenant = Depends(require_superadmin)):
#       ...
# =============================================================================

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Tenant, TenantStatus
from app.security import decode_access_token


# =============================================================================
# Esquema OAuth2 (Bearer Token)
# =============================================================================
# Define o endpoint de login para o Swagger UI e o esquema de autenticação.
# O tokenUrl aponta para a rota de login que retorna o token JWT.
# =============================================================================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# =============================================================================
# Dependência: Obter Tenant Autenticado
# =============================================================================
async def get_current_tenant(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Tenant:
    """
    Extrai e valida o tenant autenticado a partir do token JWT.

    Fluxo de validação:
        1. Decodifica o token JWT (verifica assinatura e expiração).
        2. Extrai o tenant_id (claim 'sub') do payload.
        3. Busca o tenant no banco de dados.
        4. Verifica se o tenant existe e está ativo.

    Args:
        token: Token JWT do header Authorization (injetado automaticamente).
        db: Sessão do banco de dados (injetada automaticamente).

    Returns:
        Objeto Tenant do banco de dados.

    Raises:
        HTTPException 401: Token inválido, expirado ou tenant não encontrado.
        HTTPException 403: Conta suspensa ou inativa.
    """
    # Exceção padrão para credenciais inválidas
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado. Faça login novamente.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Decodifica o token JWT
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    # 2. Extrai o tenant_id do payload
    tenant_id: str = payload.get("sub")
    if tenant_id is None:
        raise credentials_exception

    # 3. Busca o tenant no banco de dados
    result = await db.execute(
        select(Tenant).where(Tenant.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()

    # 4. Verifica se o tenant existe
    if tenant is None:
        raise credentials_exception

    # 5. Verifica se a conta está ativa
    if tenant.status == TenantStatus.SUSPENDED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta suspensa. Entre em contato com o suporte.",
        )

    if tenant.status == TenantStatus.INACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta inativa. Reative sua conta para continuar.",
        )

    return tenant


# =============================================================================
# Dependência: Apenas Super-Admin
# =============================================================================
async def require_superadmin(
    tenant: Tenant = Depends(get_current_tenant),
) -> Tenant:
    """
    Exige que o usuário autenticado seja o Super-Admin.

    Usa get_current_tenant como base e adiciona validação de permissão.
    Apenas os endpoints de gestão da plataforma (gestão de clientes,
    dashboard global, etc.) devem usar esta dependência.

    Args:
        tenant: Tenant autenticado (injetado via get_current_tenant).

    Returns:
        Objeto Tenant do Super-Admin.

    Raises:
        HTTPException 403: Usuário não é Super-Admin.
    """
    if not tenant.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas o administrador pode acessar este recurso.",
        )
    return tenant
