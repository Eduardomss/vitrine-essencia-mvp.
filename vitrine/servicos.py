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


def montar_mensagem_carrinho(itens, link_pedido=None):
    linhas = ["Olá! Quero fazer um pedido:"]
    for i in itens:
        p = i["produto"]
        linhas.append(
            f"{i['qtd']}x {p.nome} (R$ {formatar_reais(p.preco)} cada) = R$ {formatar_reais(i['subtotal'])}"
        )
    linhas.append(f"Total: R$ {formatar_reais(total_dos_itens(itens))}")
    if link_pedido:
        linhas.append(f"Pedido: {link_pedido}")
    return "\n".join(linhas)


def montar_link_carrinho(itens):
    texto = quote(montar_mensagem_carrinho(itens))
    return f"https://wa.me/{settings.WHATSAPP_NUMERO}?text={texto}"


def criar_pedido(itens):
    """Grava o pedido (com cópia dos itens) a partir dos itens do carrinho."""
    from django.db import transaction

    from .models import ItemPedido, Pedido

    with transaction.atomic():
        pedido = Pedido.objects.create(total=total_dos_itens(itens))
        ItemPedido.objects.bulk_create(
            [ItemPedido(pedido=pedido, nome=i["produto"].nome, preco=i["produto"].preco, qtd=i["qtd"]) for i in itens]
        )
    return pedido


def montar_mensagem_pedido(pedido, link_pedido):
    linhas = [f"Olá! Fiz o pedido {pedido.numero}:"]
    for i in pedido.itens.all():
        linhas.append(f"{i.qtd}x {i.nome} (R$ {formatar_reais(i.preco)} cada) = R$ {formatar_reais(i.subtotal)}")
    linhas.append(f"Total: R$ {formatar_reais(pedido.total)}")
    linhas.append(f"Detalhes e pagamento: {link_pedido}")
    return "\n".join(linhas)


def montar_link_pedido_whatsapp(pedido, link_pedido):
    texto = quote(montar_mensagem_pedido(pedido, link_pedido))
    return f"https://wa.me/{settings.WHATSAPP_NUMERO}?text={texto}"


def pix_do_pedido(pedido):
    """Texto do Pix copia e cola do pedido, ou None se a loja não configurou a chave."""
    if not settings.PIX_CHAVE:
        return None
    from .pix import montar_pix

    return montar_pix(settings.PIX_CHAVE, settings.PIX_NOME, settings.PIX_CIDADE, pedido.total, pedido.codigo)
