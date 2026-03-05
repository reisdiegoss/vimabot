# =============================================================================
# VimaBOT SaaS - Schemas de Configuração do Bot
# =============================================================================
# Schemas Pydantic para configuração do bot Telegram de cada tenant.
# =============================================================================

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# =============================================================================
# Schema de Criação/Atualização (POST/PUT)
# =============================================================================
class BotConfigUpdate(BaseModel):
    """
    Schema para configurar ou atualizar o bot de um tenant.

    O tenant preenche este formulário no painel para configurar:
    - Token do bot Telegram (obtido no @BotFather).
    - Credenciais de pagamento (Vimapix e/ou OpenPix).
    - Credenciais do Minio S3 (endpoint, chaves de acesso, bucket).
    """
    # --- Bot Telegram ---
    bot_token: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Token do bot Telegram (@BotFather)",
        examples=["123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"],
    )
    bot_username: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Username do bot (sem @)",
        examples=["meu_bot_vendas"],
    )

    # --- Pagamento Vimapix (Manual) ---
    vimapix_key: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Chave PIX do tenant para QR Codes Vimapix",
        examples=["pix@empresa.com"],
    )
    vimapix_beneficiary_name: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Nome do beneficiário no QR Code PIX",
        examples=["João Silva"],
    )
    vimapix_beneficiary_city: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Cidade do beneficiário no QR Code PIX",
        examples=["São Paulo"],
    )

    # --- Pagamento OpenPix (Automático) ---
    openpix_apikey: Optional[str] = Field(
        default=None,
        max_length=255,
        description="API Key do OpenPix para webhooks automáticos",
    )

    # --- Minio S3 (Storage) ---
    minio_endpoint: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Endpoint do Minio S3",
        examples=["s3.vimasistemas.com.br"],
    )
    minio_access_key: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Access Key do Minio",
    )
    minio_secret_key: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Secret Key do Minio",
    )
    minio_bucket: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Nome do bucket S3",
        examples=["vimabot"],
    )


# =============================================================================
# Schema de Resposta (GET)
# =============================================================================
class BotConfigResponse(BaseModel):
    """
    Schema de resposta com a configuração do bot.

    Campos sensíveis (tokens, api keys, secret keys) são mascarados
    na resposta para segurança. Apenas os últimos 4 caracteres são exibidos.
    """
    id: uuid.UUID = Field(..., description="ID da configuração")
    tenant_id: uuid.UUID = Field(..., description="ID do tenant")
    bot_token_masked: Optional[str] = Field(None, description="Token mascarado")
    bot_username: Optional[str] = Field(None, description="Username do bot")
    is_running: bool = Field(..., description="Se o bot está rodando")
    vimapix_key: Optional[str] = Field(None, description="Chave PIX do tenant")
    vimapix_beneficiary_name: Optional[str] = Field(None, description="Nome do beneficiário")
    vimapix_beneficiary_city: Optional[str] = Field(None, description="Cidade do beneficiário")
    openpix_configured: bool = Field(False, description="Se OpenPix está configurado")
    minio_endpoint: Optional[str] = Field(None, description="Endpoint Minio")
    minio_bucket: Optional[str] = Field(None, description="Bucket Minio")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")

    model_config = {"from_attributes": True}
