# =============================================================================
# VimaBOT SaaS - Schemas de Tenant
# =============================================================================
# Schemas Pydantic para CRUD de tenants (clientes da plataforma).
# Usados para validação de entrada e serialização de saída nas rotas.
# =============================================================================

import uuid
from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models import PlanType, TenantStatus


# =============================================================================
# Schema Base (campos compartilhados)
# =============================================================================
class TenantBase(BaseModel):
    """Campos compartilhados entre criação e resposta de tenants."""
    company_name: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Nome da empresa ou razão social",
        examples=["Minha Empresa LTDA"],
    )
    owner_email: EmailStr = Field(
        ...,
        description="Email do proprietário (login)",
        examples=["contato@empresa.com"],
    )


# =============================================================================
# Schema de Criação (POST)
# =============================================================================
class TenantCreate(TenantBase):
    """
    Schema para criação de um novo tenant.

    O Super-Admin usa este schema para onboarding de novos clientes.
    A senha será hasheada com bcrypt antes de salvar no banco.
    """
    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="Senha da conta (mínimo 6 caracteres)",
        examples=["senha_segura_123"],
    )
    plan_type: PlanType = Field(
        default=PlanType.FREE,
        description="Tipo de plano: free, basic, premium, enterprise",
    )
    subscription_due_date: Optional[date] = Field(
        default=None,
        description="Data de vencimento da assinatura (None = plano free)",
        examples=["2026-12-31"],
    )


# =============================================================================
# Schema de Atualização (PUT/PATCH)
# =============================================================================
class TenantUpdate(BaseModel):
    """
    Schema para atualização parcial de um tenant.

    Todos os campos são opcionais — apenas os fornecidos serão atualizados.
    O Super-Admin pode alterar plano, status e data de vencimento.
    """
    company_name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=200,
        description="Novo nome da empresa",
    )
    owner_email: Optional[EmailStr] = Field(
        default=None,
        description="Novo email do proprietário",
    )
    plan_type: Optional[PlanType] = Field(
        default=None,
        description="Novo tipo de plano",
    )
    status: Optional[TenantStatus] = Field(
        default=None,
        description="Novo status: active, inactive, suspended",
    )
    subscription_due_date: Optional[date] = Field(
        default=None,
        description="Nova data de vencimento da assinatura",
    )
    password: Optional[str] = Field(
        default=None,
        min_length=6,
        max_length=128,
        description="Nova senha (será hasheada com bcrypt)",
    )


# =============================================================================
# Schema de Resposta (GET)
# =============================================================================
class TenantResponse(TenantBase):
    """
    Schema de resposta para exibição de dados do tenant.

    Nunca inclui a senha ou hash da senha por segurança.
    Inclui o status do bot (se configurado) para o dashboard.
    """
    id: uuid.UUID = Field(
        ...,
        description="ID único do tenant",
    )
    plan_type: PlanType = Field(
        ...,
        description="Plano atual do tenant",
    )
    status: TenantStatus = Field(
        ...,
        description="Status da conta",
    )
    subscription_due_date: Optional[date] = Field(
        default=None,
        description="Data de vencimento da assinatura",
    )
    is_superadmin: bool = Field(
        ...,
        description="True se é Super-Admin",
    )
    created_at: datetime = Field(
        ...,
        description="Data de criação",
    )
    updated_at: datetime = Field(
        ...,
        description="Última atualização",
    )

    model_config = {"from_attributes": True}


# =============================================================================
# Schema de Lista (GET /tenants)
# =============================================================================
class TenantListResponse(BaseModel):
    """Schema de resposta para listagem paginada de tenants."""
    tenants: list[TenantResponse] = Field(
        ...,
        description="Lista de tenants",
    )
    total: int = Field(
        ...,
        description="Total de registros encontrados",
    )
