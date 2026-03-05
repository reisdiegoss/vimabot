# =============================================================================
# VimaBOT SaaS - Schemas de Autenticação
# =============================================================================
# Schemas Pydantic para as rotas de login e resposta de autenticação.
# =============================================================================

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """
    Schema de requisição de login.

    Campos:
        email: Email do tenant (usado como username).
        password: Senha em texto plano.
    """
    email: EmailStr = Field(
        ...,
        description="Email do proprietário da conta",
        examples=["tenant@exemplo.com"],
    )
    password: str = Field(
        ...,
        min_length=6,
        description="Senha da conta (mínimo 6 caracteres)",
        examples=["minha_senha_123"],
    )


class TokenResponse(BaseModel):
    """
    Schema de resposta do login com o token JWT.

    Campos:
        access_token: Token JWT para usar no header Authorization.
        token_type: Tipo do token (sempre "bearer").
        tenant_id: ID do tenant autenticado.
        email: Email do tenant.
        company_name: Nome da empresa do tenant.
        is_superadmin: Se o tenant é Super-Admin.
    """
    access_token: str = Field(
        ...,
        description="Token JWT para autenticação nas rotas protegidas",
    )
    token_type: str = Field(
        default="bearer",
        description="Tipo do token (sempre 'bearer')",
    )
    tenant_id: str = Field(
        ...,
        description="UUID do tenant autenticado",
    )
    email: str = Field(
        ...,
        description="Email do tenant",
    )
    company_name: str = Field(
        ...,
        description="Nome da empresa do tenant",
    )
    is_superadmin: bool = Field(
        ...,
        description="True se o tenant é Super-Admin da plataforma",
    )
