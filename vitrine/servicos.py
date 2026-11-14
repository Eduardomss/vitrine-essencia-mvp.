"""Regras de negócio do pedido pelo WhatsApp (RF02)."""
from urllib.parse import quote

from django.conf import settings

QTD_MIN = 1
QTD_MAX = 99


def formatar_reais(valor):
    """Formata um valor no padrão brasileiro: 51,00."""
    return f"{valor:.2f}".replace(".", ",")


def limpar_quantidade(texto):
    """Converte o texto digitado em quantidade válida (entre 1 e 99)."""
    try:
        qtd = int(texto)
    except (TypeError, ValueError):
        return QTD_MIN
    return max(QTD_MIN, min(qtd, QTD_MAX))


def montar_mensagem(produto, qtd):
    total = produto.preco * qtd
    return (
        f"Olá! Quero fazer um pedido:\n"
        f"{qtd}x {produto.nome} (R$ {formatar_reais(produto.preco)} cada)\n"
        f"Total: R$ {formatar_reais(total)}"
    )


def montar_link_whatsapp(produto, qtd):
    texto = quote(montar_mensagem(produto, qtd))
    return f"https://wa.me/{settings.WHATSAPP_NUMERO}?text={texto}"
