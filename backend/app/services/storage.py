# =============================================================================
# VimaBOT SaaS - Serviço de Storage (S3 / Minio)
# =============================================================================
# Responsável pelo upload, download e geração de URLs assinadas (presigned)
# utilizando o Minio S3 de forma assíncrona (aiobotocore).
#
# A Zero-URL Policy preconiza que os links restritos aos arquivos NUNCA cheguem
# diretamente ao comprador. O servidor baixa do S3 e envia no chat do Telegram.
# =============================================================================

import os
from typing import Optional
from contextlib import asynccontextmanager

from aiobotocore.session import get_session


class StorageService:
    """
    Serviço assíncrono para interagir com o Minio ou AWS S3.
    """

    def __init__(
        self,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        use_ssl: bool = True
    ):
        self.endpoint_url = endpoint_url
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.use_ssl = use_ssl
        self.session = get_session()

        # O endpoint precisa ter https:// ou http://
        scheme = "https://" if self.use_ssl else "http://"
        if not self.endpoint_url.startswith("http"):
            self.endpoint_url = f"{scheme}{self.endpoint_url}"

    @asynccontextmanager
    async def _get_client(self):
        """Context manager para gerenciar o client assíncrono do aiobotocore."""
        async with self.session.create_client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        ) as client:
            yield client

    async def upload_file(self, content: bytes, object_name: str) -> bool:
        """
        Faz upload de um arquivo para o bucket S3 em memória (bytes).

        Args:
            content: O conteúdo do arquivo em bytes.
            object_name: O caminho/chave de destino (ex: 'tenant-1/products/file.mp4').
        """
        async with self._get_client() as client:
            try:
                await client.put_object(
                    Bucket=self.bucket_name,
                    Key=object_name,
                    Body=content
                )
                return True
            except Exception as e:
                print(f"[StorageService] Erro ao fazer upload do arquivo {object_name}: {e}")
                return False

    async def upload_file_from_disk(self, file_path: str, object_name: str) -> bool:
        """
        Faz upload de um arquivo salvo em disco para o S3.
        """
        if not os.path.exists(file_path):
            return False

        try:
            with open(file_path, "rb") as f:
                content = f.read()
            return await self.upload_file(content, object_name)
        except Exception as e:
            print(f"[StorageService] Erro carregando do disco {file_path}: {e}")
            return False

    async def get_file(self, object_name: str) -> Optional[bytes]:
        """
        Baixa o conteúdo de um arquivo do S3 para a memória.
        Utilizado para a política Zero-URL, onde o back-end baixa e repassa para o Telegram.
        """
        async with self._get_client() as client:
            try:
                response = await client.get_object(
                    Bucket=self.bucket_name,
                    Key=object_name
                )
                async with response['Body'] as stream:
                    content = await stream.read()
                return content
            except Exception as e:
                print(f"[StorageService] Erro ao baixar arquivo {object_name}: {e}")
                return None

    async def generate_presigned_url(self, object_name: str, expiration: int = 3600) -> Optional[str]:
        """
        Gera uma URL temporária (assinada) para visualizar/baixar o arquivo.
        Pode ser usado pelo painel para o Super-Admin/Tenant inspecionar os arquivos.
        """
        async with self._get_client() as client:
            try:
                url = await client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': object_name},
                    ExpiresIn=expiration
                )
                return url
            except Exception as e:
                print(f"[StorageService] Erro ao gerar URL para {object_name}: {e}")
                return None

    async def delete_file(self, object_name: str) -> bool:
        """
        Remove um arquivo do bucket S3.
        """
        async with self._get_client() as client:
            try:
                await client.delete_object(
                    Bucket=self.bucket_name,
                    Key=object_name
                )
                return True
            except Exception as e:
                print(f"[StorageService] Erro ao deletar arquivo {object_name}: {e}")
                return False
