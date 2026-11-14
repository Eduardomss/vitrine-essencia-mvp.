from django.shortcuts import render

from .models import Produto


def vitrine(request):
    """Vitrine pública: lista apenas os produtos marcados como visíveis (RF01)."""
    produtos = Produto.objects.filter(visivel=True)
    return render(request, "vitrine/lista.html", {"produtos": produtos})
