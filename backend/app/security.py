# =============================================================================
# VimaBOT SaaS - Segurança (JWT + Hashing de Senhas)
# =============================================================================
# Módulo centralizado de segurança da plataforma.
#
# Responsabilidades:
#   - Criação e verificação de tokens JWT (JSON Web Token).
#   - Hashing e verificação de senhas com bcrypt.
#
# O JWT carrega o ID do tenant e a flag is_superadmin no payload,
# permitindo autenticação e autorização em um único token.
# =============================================================================

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings


# =============================================================================
# Contexto de Hashing de Senhas (bcrypt)
# =============================================================================
# bcrypt é o algoritmo recomendado para hashing de senhas:
#   - Resistente a ataques de força bruta (salt automático).
#   - Custo computacional ajustável (rounds).
#   - deprecated="auto" mantém compatibilidade com hashes antigos.
# =============================================================================
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """
    Gera o hash bcrypt de uma senha em texto plano.

    Args:
        password: Senha em texto plano fornecida pelo usuário.

    Returns:
        Hash bcrypt da senha (string de ~60 caracteres).

    Exemplo:
        >>> hash_password("minha_senha_123")
        '$2b$12$...'
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se uma senha em texto plano corresponde ao hash armazenado.

    Args:
        plain_password: Senha digitada pelo usuário.
        hashed_password: Hash bcrypt armazenado no banco de dados.

    Returns:
        True se a senha está correta, False caso contrário.

    Exemplo:
        >>> verify_password("minha_senha_123", hash_armazenado)
        True
    """
    return pwd_context.verify(plain_password, hashed_password)


# =============================================================================
# Criação de Tokens JWT
# =============================================================================
def create_access_token(
    tenant_id: str,
    email: str,
    is_superadmin: bool = False,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Cria um token JWT de acesso para autenticação na API.

    O token carrega no payload (claims):
        - sub: ID do tenant (UUID como string).
        - email: Email do tenant (para display no frontend).
        - is_superadmin: Flag de Super-Admin (para autorização).
        - exp: Data de expiração do token.

    Args:
        tenant_id: UUID do tenant autenticado (como string).
        email: Email do tenant.
        is_superadmin: True se o tenant é Super-Admin.
        expires_delta: Tempo personalizado de expiração (opcional).
                       Se None, usa JWT_ACCESS_TOKEN_EXPIRE_MINUTES do .env.

    Returns:
        Token JWT assinado (string codificada).

    Exemplo:
        >>> token = create_access_token(
        ...     tenant_id="abc-123",
        ...     email="tenant@exemplo.com",
        ...     is_superadmin=False,
        ... )
    """
    # Define o tempo de expiração do token
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )

    # Monta o payload do token com os claims
    to_encode = {
        "sub": tenant_id,          # Subject: ID do tenant
        "email": email,            # Email para display
        "is_superadmin": is_superadmin,  # Flag de autorização
        "exp": expire,             # Expiração
    }

    # Codifica e assina o token com a chave secreta
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    return encoded_jwt


# =============================================================================
# Decodificação e Verificação de Tokens JWT
# =============================================================================
def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodifica e verifica um token JWT.

    Valida automaticamente:
        - Assinatura (chave secreta).
        - Expiração (claim 'exp').

    Args:
        token: Token JWT recebido no header Authorization.

    Returns:
        Dicionário com os claims do payload se o token é válido.
        None se o token é inválido ou expirou.

    Exemplo:
        >>> payload = decode_access_token("eyJ...")
        >>> if payload:
        ...     tenant_id = payload["sub"]
        ...     is_admin = payload["is_superadmin"]
    """
    try:
        # Decodifica o token verificando assinatura e expiração
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError:
        # Token inválido, expirado ou adulterado
        return None
