# =============================================================================
# VimaBOT SaaS - Serviço PIX
# =============================================================================
# Centraliza a lógica de geração de pagamentos e validação de Webhooks.
# Suporta a geração do código Pix Copia e Cola (BR Code) e o roteamento 
# para o gateway escolhido (Manual / OpenPix).
# =============================================================================

import uuid
import httpx
from typing import Optional, Dict

from app.config import settings
from app.models import BotConfig


class PixService:
    """
    Serviço central de integração de PIX.
    Gera as faturas dependendo de como o Tenant configurou seu bot.
    """

    @staticmethod
    async def generate_manual_pix(
        tenant_config: BotConfig,
        order_id: uuid.UUID,
        total_amount: float
    ) -> Optional[str]:
        """
        Gera o código PIX Copia e Cola usando a API REST Vimapix.
        (A configuração da API URL Vimapix está no .env / config do Super-Admin).
        
        Args:
            tenant_config: As configurações do tenant (BotConfig) contendo chaves, cidade e nome.
            order_id: O ID do pedido para amarrar à transação
            total_amount: O valor do pedido.
            
        Returns:
            String contendo o código PIX copia e cola, ou None em caso de falha.
        """
        if not tenant_config.vimapix_key:
            return None

        # Prepara a chamada usando o gateway do Vimapix gerador.
        # Usa os dados do bot_config do tenant.
        payload = {
            "key": tenant_config.vimapix_key,
            "name": tenant_config.vimapix_beneficiary_name or "VimaBOT Loja",
            "city": tenant_config.vimapix_beneficiary_city or "BRASIL",
            "amount": float(total_amount),
            "reference": str(order_id)[:20],  # TXID/Reference no PIX é geralmente string curta
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.vimapix_api_url, 
                    json=payload,
                    timeout=5.0
                )
                response.raise_for_status()
                data = response.json()
                
                # A api vimapix deve retornar um json e um payload
                # Exemplo esperado: {"payload": "0002010...BRCODE"}
                return data.get("payload")
            
        except Exception as e:
            print(f"[PixService] Falha ao gerar Vimapix Manual para a Ordem {order_id}: {e}")
            return None

    @staticmethod
    async def generate_webhook_payment(
        tenant_config: BotConfig,
        order_id: uuid.UUID,
        customer_name: str,
        total_amount: float
    ) -> Dict[str, str]:
        """
        Gera uma fatura dinâmica na OpenPix. (Para automação de webhook).
        (Stub: A ser implementado. Depende da estrutura de rotas da OpenPix).
        """
        if not tenant_config.openpix_apikey:
            return {"status": "error", "message": "API do OpenPix não configurada."}
            
        # TODO: Fazer chamada HTTP para OpenPix passando a APIKey do Tenant. 
        # Headers: {"Authorization": tenant_config.openpix_apikey}
        
        return {
            "status": "pending",
            "checkout_url": "https://...",
            "brcode": "000201....",
            "correlation_id": "OPENPIX_ID_AQUI"
        }
