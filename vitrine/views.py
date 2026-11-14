from django.shortcuts import get_object_or_404, render

from . import servicos
from .models import Produto


def vitrine(request):
    """Vitrine pública: lista apenas os produtos marcados como visíveis (RF01)."""
    produtos = Produto.objects.filter(visivel=True)
    return render(request, "vitrine/lista.html", {"produtos": produtos})


def pedido(request, pk):
    """Tela de pedido: escolhe a quantidade e abre o WhatsApp com a mensagem pronta (RF02)."""
    produto = get_object_or_404(Produto, pk=pk, visivel=True)
    qtd = servicos.limpar_quantidade(request.GET.get("qtd", "1"))
    contexto = {
        "produto": produto,
        "qtd": qtd,
        "total": servicos.formatar_reais(produto.preco * qtd),
        "link_whatsapp": servicos.montar_link_whatsapp(produto, qtd),
    }
    return render(request, "vitrine/pedido.html", contexto)
