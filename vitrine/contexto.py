from django.conf import settings

from . import servicos


def loja(request):
    """Disponibiliza o nome da loja e a quantidade do pedido em todos os templates."""
    carrinho = request.session.get("carrinho", {}) if hasattr(request, "session") else {}
    return {"LOJA_NOME": settings.LOJA_NOME, "QTD_PEDIDO": servicos.quantidade_total(carrinho)}
