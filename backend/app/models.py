# =============================================================================
# VimaBOT SaaS - Modelos de Dados (SQLAlchemy Async)
# =============================================================================
# Definição completa do esquema multi-tenant do banco de dados PostgreSQL.
#
# Estratégia Multi-Tenant:
#   Discriminador por coluna (tenant_id). Todas as tabelas de negócio
#   possuem tenant_id como FK, garantindo isolamento lógico dos dados.
#
# Tabelas:
#   - tenants:       Clientes da plataforma (e o Super-Admin).
#   - bot_configs:   Configurações do bot Telegram de cada tenant.
#   - products:      Catálogo de produtos digitais por tenant.
#   - orders:        Pedidos de compra com status Kanban.
#   - managed_chats: Grupos/canais do Telegram gerenciados pelo bot.
#
# Convenções:
#   - IDs primários: UUID v4 (gerados automaticamente).
#   - Timestamps: created_at e updated_at em todas as tabelas.
#   - Soft delete: Não implementado (usar status/is_active para desativar).
#   - Enums: Tipos PostgreSQL nativos para status e planos.
# =============================================================================

import uuid
from datetime import datetime, date
from enum import Enum as PyEnum

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Date,
    Numeric,
    BigInteger,
    Integer,
    Text,
    ForeignKey,
    Enum,
    func,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database import Base


# =============================================================================
# Enumerações (Postgres Native Enums)
# =============================================================================
# Enums nativos do PostgreSQL garantem integridade dos dados no nível do banco.
# Apenas valores válidos são aceitos, sem necessidade de validação na aplicação.
# =============================================================================


class PlanType(str, PyEnum):
    """
    Tipos de plano disponíveis para os tenants.

    Valores:
        free:       Plano gratuito com funcionalidades limitadas.
        basic:      Plano básico com funcionalidades essenciais.
        premium:    Plano premium com todas as funcionalidades.
        enterprise: Plano empresarial com suporte dedicado.
    """
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class TenantStatus(str, PyEnum):
    """
    Status possíveis de um tenant na plataforma.

    Valores:
        active:    Conta ativa, bot funcionando normalmente.
        inactive:  Conta inativa (desativada voluntariamente).
        suspended: Conta suspensa (inadimplência ou violação).
    """
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class OrderStatus(str, PyEnum):
    """
    Status de um pedido no fluxo Kanban.

    Fluxo normal:
        pending → validation → paid → delivered

    Valores:
        pending:    Aguardando pagamento (QR Code PIX gerado).
        validation: Comprovante enviado, aguardando validação do tenant.
        paid:       Pagamento confirmado (manual pelo tenant ou webhook OpenPix).
        delivered:  Arquivo digital entregue ao comprador via Telegram.
    """
    PENDING = "pending"
    VALIDATION = "validation"
    PAID = "paid"
    DELIVERED = "delivered"


# =============================================================================
# Modelo: Tenants (Clientes da Plataforma)
# =============================================================================
class Tenant(Base):
    """
    Representa um cliente (inquilino) da plataforma VimaBOT SaaS.

    Cada tenant é uma empresa/pessoa que aluga uma instância de bot do
    Telegram para vender seus produtos digitais. O Super-Admin é um
    tenant especial com a flag is_superadmin=True.

    O campo subscription_due_date controla o vencimento da assinatura.
    Quando vencido, o sistema pode suspender automaticamente o bot e
    bloquear o acesso ao painel.

    Relacionamentos:
        - bot_config:    Configuração do bot Telegram (1:1).
        - products:      Lista de produtos digitais (1:N).
        - orders:        Lista de pedidos de compra (1:N).
        - managed_chats: Grupos/canais gerenciados (1:N).
    """
    __tablename__ = "tenants"

    # --- Identificação ---
    # UUID v4 gerado automaticamente como chave primária
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único do tenant (UUID v4)",
    )

    # --- Dados da Empresa ---
    # Nome da empresa do tenant (exibido no painel e nas cobranças)
    company_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Nome da empresa ou razão social do tenant",
    )

    # Email do proprietário (usado para login e comunicação)
    owner_email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="Email do proprietário (login único na plataforma)",
    )

    # Hash da senha (bcrypt via passlib)
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Hash bcrypt da senha do proprietário",
    )

    # --- Plano e Status ---
    # Tipo de plano contratado pelo tenant
    plan_type: Mapped[PlanType] = mapped_column(
        Enum(PlanType, name="plan_type_enum", create_type=True),
        nullable=False,
        default=PlanType.FREE,
        comment="Tipo de plano: free, basic, premium, enterprise",
    )

    # Status atual da conta do tenant
    status: Mapped[TenantStatus] = mapped_column(
        Enum(TenantStatus, name="tenant_status_enum", create_type=True),
        nullable=False,
        default=TenantStatus.ACTIVE,
        comment="Status da conta: active, inactive, suspended",
    )

    # --- Controle de Assinatura ---
    # Data de vencimento da assinatura do tenant.
    # Se None, o tenant está no plano gratuito (sem vencimento).
    # Se a data estiver no passado, o sistema pode suspender o bot.
    subscription_due_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        default=None,
        comment="Data de vencimento da assinatura (None = plano free)",
    )

    # --- Permissões ---
    # Flag que identifica o Super-Admin (dono da plataforma).
    # Apenas 1 registro deve ter is_superadmin=True.
    is_superadmin: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="True se este tenant é o Super-Admin da plataforma",
    )

    # --- Timestamps ---
    # Data de criação do registro (preenchida automaticamente pelo banco)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Data e hora de criação do registro",
    )

    # Data da última atualização (atualizada automaticamente pelo banco)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Data e hora da última atualização",
    )

    # --- Relacionamentos ORM ---
    # Configuração do bot Telegram (relação 1:1)
    # uselist=False garante que retorna um objeto, não uma lista
    bot_config: Mapped["BotConfig | None"] = relationship(
        "BotConfig",
        back_populates="tenant",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Lista de produtos digitais do tenant (relação 1:N)
    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates="tenant",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Lista de pedidos de compra do tenant (relação 1:N)
    orders: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="tenant",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Lista de chats/grupos gerenciados pelo bot (relação 1:N)
    managed_chats: Mapped[list["ManagedChat"]] = relationship(
        "ManagedChat",
        back_populates="tenant",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """Representação textual do tenant para logs e debug."""
        return (
            f"<Tenant(id={self.id}, company='{self.company_name}', "
            f"email='{self.owner_email}', plan='{self.plan_type.value}', "
            f"status='{self.status.value}')>"
        )


# =============================================================================
# Modelo: BotConfigs (Configuração do Bot Telegram)
# =============================================================================
class BotConfig(Base):
    """
    Configurações do bot Telegram de um tenant específico.

    Cada tenant possui exatamente 1 configuração de bot (relação 1:1).
    Armazena o token do bot, credenciais de pagamento e storage S3.

    O campo is_running controla se o bot está ativo ou parado.
    O Super-Admin pode parar o bot de um tenant inadimplente.

    Segurança:
        - bot_token, vimapix_key, openpix_apikey e minio_secret_key são
          dados sensíveis. Em produção, considere criptografia at-rest.
        - Cada tenant tem suas próprias credenciais S3 isoladas.
    """
    __tablename__ = "bot_configs"

    # --- Identificação ---
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único da configuração do bot",
    )

    # FK para o tenant proprietário do bot (relação 1:1)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
        comment="ID do tenant proprietário deste bot",
    )

    # --- Telegram Bot ---
    # Token fornecido pelo @BotFather do Telegram
    bot_token: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Token do bot Telegram (fornecido pelo @BotFather)",
    )

    # Username do bot (sem @), usado para gerar links t.me/
    bot_username: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Username do bot no Telegram (sem @)",
    )

    # Flag que indica se o bot está rodando ou parado
    is_running: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="True se o bot está ativo e respondendo no Telegram",
    )

    # --- Credenciais de Pagamento ---
    # Chave PIX do tenant (usada na integração Vimapix para pagamento manual)
    vimapix_key: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Chave PIX do tenant para geração de QR Code via Vimapix",
    )

    # Nome do beneficiário PIX (exibido no QR Code)
    vimapix_beneficiary_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Nome do beneficiário exibido no QR Code PIX",
    )

    # Cidade do beneficiário PIX (exibida no QR Code)
    vimapix_beneficiary_city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Cidade do beneficiário exibida no QR Code PIX",
    )

    # API Key do OpenPix (para integração automática de pagamento)
    openpix_apikey: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="API Key do OpenPix para webhooks automáticos de pagamento",
    )

    # --- Credenciais Minio S3 ---
    # Endpoint do serviço Minio do tenant (pode ser diferente do padrão)
    minio_endpoint: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Endpoint do Minio S3 do tenant",
    )

    # Access Key para autenticação no Minio
    minio_access_key: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Access Key do Minio S3 do tenant",
    )

    # Secret Key para autenticação no Minio
    minio_secret_key: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Secret Key do Minio S3 do tenant (dado sensível)",
    )

    # Nome do bucket onde os arquivos do tenant são armazenados
    minio_bucket: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Nome do bucket S3 do tenant",
    )

    # --- Timestamps ---
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Data e hora de criação do registro",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Data e hora da última atualização",
    )

    # --- Relacionamento ORM ---
    # Referência reversa para o tenant proprietário
    tenant: Mapped["Tenant"] = relationship(
        "Tenant",
        back_populates="bot_config",
    )

    def __repr__(self) -> str:
        """Representação textual da configuração do bot."""
        return (
            f"<BotConfig(id={self.id}, tenant_id={self.tenant_id}, "
            f"bot_username='{self.bot_username}', running={self.is_running})>"
        )


# =============================================================================
# Modelo: Products (Catálogo de Produtos Digitais)
# =============================================================================
class Product(Base):
    """
    Produto digital disponível no catálogo de um tenant.

    Cada produto é um arquivo digital (filme, ebook, software, etc.)
    armazenado no Minio S3. O campo s3_key armazena o caminho completo
    do arquivo no bucket do tenant.

    O campo is_active permite desativar temporariamente um produto sem
    removê-lo do banco de dados (soft toggle).

    Nomenclatura S3:
        Os arquivos seguem o padrão: tenant-{id}/products/{nome_arquivo}
        Exemplo: tenant-abc123/products/filme_2026.mp4
    """
    __tablename__ = "products"

    # --- Identificação ---
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único do produto",
    )

    # FK para o tenant proprietário do produto
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID do tenant proprietário deste produto",
    )

    # --- Dados do Produto ---
    # Nome do produto exibido no catálogo do bot
    name: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
        comment="Nome do produto exibido no catálogo do bot",
    )

    # Descrição detalhada do produto (opcional)
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Descrição detalhada do produto (opcional)",
    )

    # Caminho do arquivo no Minio S3 (ex: tenant-abc/products/video.mp4)
    s3_key: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Caminho completo do arquivo no bucket S3 do tenant",
    )

    # Preço do produto em Reais (até R$ 99.999.999,99)
    price: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Preço do produto em R$ (Reais)",
    )

    # Flag para ativar/desativar o produto no catálogo
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="True se o produto está visível no catálogo do bot",
    )

    # --- Timestamps ---
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Data e hora de criação do registro",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Data e hora da última atualização",
    )

    # --- Relacionamentos ORM ---
    # Referência reversa para o tenant proprietário
    tenant: Mapped["Tenant"] = relationship(
        "Tenant",
        back_populates="products",
    )

    # Lista de pedidos deste produto (relação 1:N)
    orders: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="product",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """Representação textual do produto."""
        return (
            f"<Product(id={self.id}, name='{self.name}', "
            f"price={self.price}, active={self.is_active})>"
        )


# =============================================================================
# Modelo: Orders (Pedidos de Compra)
# =============================================================================
class Order(Base):
    """
    Pedido de compra de um produto digital.

    Cada pedido representa uma transação entre um comprador (usuário do
    Telegram) e um tenant (vendedor). O fluxo segue o padrão Kanban:

        pending → validation → paid → delivered

    Campos de Pagamento:
        - gateway: Identifica o método de pagamento usado ('vimapix' ou 'openpix').
        - txid: Identificador único da transação PIX.
        - comprovante_s3_key: Caminho do comprovante no S3 (apenas para Vimapix).

    Fluxo Vimapix (Manual):
        1. Pedido criado com status 'pending'
        2. Comprador envia foto do comprovante → status 'validation'
        3. Tenant valida no painel → status 'paid'
        4. Bot entrega o arquivo → status 'delivered'

    Fluxo OpenPix (Automático):
        1. Pedido criado com status 'pending'
        2. Webhook recebe pagamento → status 'paid'
        3. Bot entrega o arquivo → status 'delivered'
    """
    __tablename__ = "orders"

    # --- Identificação ---
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único do pedido",
    )

    # FK para o tenant vendedor
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID do tenant vendedor deste pedido",
    )

    # FK para o produto comprado
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID do produto comprado (pode ser null se produto foi removido)",
    )

    # --- Dados do Comprador ---
    # ID do Telegram do comprador (bigint para IDs grandes)
    customer_telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
        comment="ID do Telegram do comprador",
    )

    # Nome do comprador no Telegram (para exibição no painel)
    customer_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Nome do comprador no Telegram",
    )

    # --- Dados Financeiros ---
    # Valor total do pedido em Reais
    total_amount: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Valor total do pedido em R$ (Reais)",
    )

    # Status atual do pedido no fluxo Kanban
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="order_status_enum", create_type=True),
        nullable=False,
        default=OrderStatus.PENDING,
        comment="Status do pedido: pending, validation, paid, delivered",
    )

    # --- Dados de Pagamento ---
    # Gateway utilizado: 'vimapix' (manual) ou 'openpix' (automático)
    gateway: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Gateway de pagamento: 'vimapix' ou 'openpix'",
    )

    # Identificador único da transação PIX
    txid: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="ID único da transação PIX (txid)",
    )

    # --- Comprovante (Vimapix - Fluxo Manual) ---
    # Caminho do comprovante de pagamento no Minio S3
    # Preenchido apenas quando o comprador envia foto pelo bot
    comprovante_s3_key: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Caminho do comprovante de pagamento no S3 (fluxo Vimapix)",
    )

    # --- Timestamps ---
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Data e hora de criação do pedido",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Data e hora da última atualização do pedido",
    )

    # --- Relacionamentos ORM ---
    # Referência reversa para o tenant vendedor
    tenant: Mapped["Tenant"] = relationship(
        "Tenant",
        back_populates="orders",
    )

    # Referência reversa para o produto comprado
    product: Mapped["Product | None"] = relationship(
        "Product",
        back_populates="orders",
    )

    # --- Índices Compostos ---
    # Índice composto para busca rápida de pedidos por tenant e status
    # (usado na view Kanban do painel do tenant)
    __table_args__ = (
        Index("ix_orders_tenant_status", "tenant_id", "status"),
        Index("ix_orders_tenant_created", "tenant_id", "created_at"),
    )

    def __repr__(self) -> str:
        """Representação textual do pedido."""
        return (
            f"<Order(id={self.id}, tenant_id={self.tenant_id}, "
            f"amount={self.total_amount}, status='{self.status.value}', "
            f"gateway='{self.gateway}')>"
        )


# =============================================================================
# Modelo: ManagedChats (Grupos/Canais Gerenciados)
# =============================================================================
class ManagedChat(Base):
    """
    Grupo ou canal do Telegram gerenciado pelo bot de um tenant.

    Quando o bot é adicionado como admin em um grupo ou canal do Telegram,
    o chat é registrado aqui. Isso permite que o tenant gerencie seus
    canais de vendas diretamente pelo painel.

    Tipos de Chat:
        - group:      Grupo normal do Telegram.
        - supergroup: Supergrupo (grupo com mais de 200 membros).
        - channel:    Canal de transmissão (broadcast).
    """
    __tablename__ = "managed_chats"

    # --- Identificação ---
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único do chat gerenciado",
    )

    # ID do chat no Telegram (bigint, pode ser negativo para grupos)
    chat_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
        comment="ID do chat no Telegram (negativo para grupos)",
    )

    # FK para o tenant proprietário
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID do tenant que gerencia este chat",
    )

    # --- Dados do Chat ---
    # Título do grupo ou canal
    title: Mapped[str | None] = mapped_column(
        String(300),
        nullable=True,
        comment="Título do grupo ou canal no Telegram",
    )

    # Tipo do chat (group, supergroup, channel)
    type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Tipo do chat: group, supergroup, channel",
    )

    # Quantidade de membros do grupo/canal
    members_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        default=0,
        comment="Quantidade de membros no grupo ou canal",
    )

    # --- Timestamps ---
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Data e hora de registro do chat",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Data e hora da última atualização",
    )

    # --- Relacionamento ORM ---
    # Referência reversa para o tenant proprietário
    tenant: Mapped["Tenant"] = relationship(
        "Tenant",
        back_populates="managed_chats",
    )

    # --- Índice Composto ---
    # Garante que o mesmo chat_id não seja registrado duas vezes para o
    # mesmo tenant (um grupo pode ser compartilhado, mas cada registro
    # é único por tenant)
    __table_args__ = (
        Index("ix_managed_chats_tenant_chat", "tenant_id", "chat_id", unique=True),
    )

    def __repr__(self) -> str:
        """Representação textual do chat gerenciado."""
        return (
            f"<ManagedChat(id={self.id}, chat_id={self.chat_id}, "
            f"title='{self.title}', type='{self.type}')>"
        )
