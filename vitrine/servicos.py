"""Regras de negócio do pedido pelo WhatsApp (RF02)."""
from decimal import Decimal
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


# ---------- Pedido com vários produtos (carrinho na sessão) ----------

def adicionar(carrinho, pk, delta):
    """Soma `delta` à quantidade do produto e devolve o novo carrinho (sem alterar o original)."""
    novo = dict(carrinho)
    qtd = max(0, min(int(novo.get(str(pk), 0)) + delta, QTD_MAX))
    if qtd:
        novo[str(pk)] = qtd
    else:
        novo.pop(str(pk), None)
    return novo


def quantidade_total(carrinho):
    return sum(int(q) for q in carrinho.values())


def itens_do_carrinho(carrinho):
    """Lista os itens do pedido (só produtos ainda visíveis) com subtotal."""
    from .models import Produto

    produtos = Produto.objects.filter(visivel=True, pk__in=[int(k) for k in carrinho if str(k).isdigit()])
    itens = []
    for p in produtos:
        qtd = int(carrinho[str(p.pk)])
        itens.append({"produto": p, "qtd": qtd, "subtotal": p.preco * qtd})
    return itens


def total_dos_itens(itens):
    return sum((i["subtotal"] for i in itens), Decimal("0"))


def montar_mensagem_carrinho(itens):
    linhas = ["Olá! Quero fazer um pedido:"]
    for i in itens:
        p = i["produto"]
        linhas.append(
            f"{i['qtd']}x {p.nome} (R$ {formatar_reais(p.preco)} cada) = R$ {formatar_reais(i['subtotal'])}"
        )
    linhas.append(f"Total: R$ {formatar_reais(total_dos_itens(itens))}")
    return "\n".join(linhas)


def montar_link_carrinho(itens):
    texto = quote(montar_mensagem_carrinho(itens))
    return f"https://wa.me/{settings.WHATSAPP_NUMERO}?text={texto}"
