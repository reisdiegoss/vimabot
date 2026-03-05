# =============================================================================
# VimaBOT SaaS - Configurações da Aplicação
# =============================================================================
# Módulo de configurações centralizado usando Pydantic Settings.
# Carrega e valida automaticamente as variáveis de ambiente do arquivo .env.
#
# Pydantic Settings garante que:
# - Tipos são validados automaticamente (str, int, bool)
# - Variáveis obrigatórias geram erro claro se ausentes
# - Valores padrão são aplicados quando a variável não existe
# =============================================================================

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    Classe de configurações globais da aplicação VimaBOT SaaS.

    Todas as variáveis de ambiente são mapeadas automaticamente.
    O prefixo é case-insensitive: DATABASE_URL ou database_url funcionam.

    Atributos:
        Banco de Dados:
            database_url: URL completa de conexão PostgreSQL (asyncpg).
            postgres_db: Nome do banco de dados.
            postgres_user: Usuário do PostgreSQL.
            postgres_password: Senha do PostgreSQL.
            postgres_host: Host do PostgreSQL.
            postgres_port: Porta do PostgreSQL.

        Minio S3 (Storage):
            minio_endpoint: Endpoint do serviço Minio.
            minio_access_key: Chave de acesso raiz do Minio.
            minio_secret_key: Chave secreta raiz do Minio.
            minio_bucket: Nome do bucket padrão.
            minio_use_ssl: Se deve usar HTTPS para conexão.

        JWT (Autenticação):
            jwt_secret_key: Chave secreta para assinar os tokens JWT.
            jwt_algorithm: Algoritmo de assinatura (HS256 por padrão).
            jwt_access_token_expire_minutes: Tempo de expiração do token.

        Vimapix (Pagamento PIX Manual):
            vimapix_api_url: URL da API Vimapix para geração de QR Code.

        Aplicação:
            app_name: Nome da aplicação exibido na API.
            app_env: Ambiente atual (development, staging, production).
            app_debug: Modo debug habilitado ou não.
            app_host: Host de bind do servidor.
            app_port: Porta do servidor.

        Super Admin (Seed):
            superadmin_email: Email do Super-Admin inicial.
            superadmin_password: Senha do Super-Admin inicial.
            superadmin_company: Nome da empresa do Super-Admin.
    """

    # -------------------------------------------------------------------------
    # Banco de Dados PostgreSQL (Serviço Externo)
    # -------------------------------------------------------------------------
    database_url: str = "postgresql+asyncpg://vimabot:vimabot_secret_2026@localhost:5432/vimabot_db"
    postgres_db: str = "vimabot_db"
    postgres_user: str = "vimabot"
    postgres_password: str = "vimabot_secret_2026"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    # -------------------------------------------------------------------------
    # Minio S3 - Armazenamento de Objetos (Serviço Externo)
    # -------------------------------------------------------------------------
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "vimabot"
    minio_secret_key: str = "vimabot123"
    minio_bucket: str = "vimabot-files"
    minio_use_ssl: bool = False

    # -------------------------------------------------------------------------
    # JWT - Autenticação por Token
    # -------------------------------------------------------------------------
    jwt_secret_key: str = "MUDE_ESTA_CHAVE_EM_PRODUCAO_vimabot_2026_super_secret"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 480  # 8 horas

    # -------------------------------------------------------------------------
    # Vimapix - Gateway PIX Manual
    # -------------------------------------------------------------------------
    vimapix_api_url: str = "https://vimapix.vimasistemas.com.br/api/generate"

    # -------------------------------------------------------------------------
    # Configurações da Aplicação
    # -------------------------------------------------------------------------
    app_name: str = "VimaBOT SaaS"
    app_env: str = "development"
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # -------------------------------------------------------------------------
    # Super Admin - Seed Inicial
    # -------------------------------------------------------------------------
    # Credenciais usadas apenas na primeira execução para criar o Super-Admin.
    superadmin_email: str = "admin@vimabot.com.br"
    superadmin_password: str = "admin123456"
    superadmin_company: str = "VimaBOT Administração"

    # -------------------------------------------------------------------------
    # Configuração do Pydantic Settings
    # -------------------------------------------------------------------------
    model_config = SettingsConfigDict(
        # Carrega variáveis do arquivo .env na raiz do projeto
        env_file=".env",
        # Ignora variáveis extras no .env que não estão mapeadas aqui
        extra="ignore",
        # Variáveis são case-insensitive (DATABASE_URL = database_url)
        case_sensitive=False,
    )

    @property
    def is_development(self) -> bool:
        """Verifica se o ambiente atual é de desenvolvimento."""
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        """Verifica se o ambiente atual é de produção."""
        return self.app_env == "production"


# =============================================================================
# Instância Global de Configurações
# =============================================================================
# Singleton reutilizado em toda a aplicação para evitar múltiplas leituras
# do arquivo .env. Importar: from app.config import settings
# =============================================================================
settings = Settings()
