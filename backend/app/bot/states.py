# =============================================================================
# VimaBOT SaaS - Estados do Bot (FSM)
# =============================================================================

from aiogram.fsm.state import State, StatesGroup


class ShopStates(StatesGroup):
    """
    Estados para a Máquina de Estados Finita (FSM) do carrinho de compras e pagamentos.
    """
    browsing = State()       # Navegando no catálogo
    in_cart = State()        # Visualizando o carrinho
    checkout = State()       # Formulário de checkout (ex: nome, cpf se necessário)
    payment_pix = State()    # Aguardando upload do comprovante (PIX Manual) ou webhook (OpenPix)
