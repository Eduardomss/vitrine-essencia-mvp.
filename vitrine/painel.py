"""Painel da proprietária: login com bloqueio e gestão de produtos (RF03 a RF06)."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProdutoForm
from .models import Pedido, Produto

MAX_TENTATIVAS = 5
BLOQUEIO_SEGUNDOS = 15 * 60


def _chave(request):
    usuario = request.POST.get("username", "").strip().lower()
    ip = request.META.get("REMOTE_ADDR", "")
    return f"login-falhas:{ip}:{usuario}"


class LoginComBloqueio(LoginView):
    """Bloqueia o login por 15 minutos após 5 tentativas erradas (RNF de segurança)."""

    template_name = "registration/login.html"

    def post(self, request, *args, **kwargs):
        if cache.get(_chave(request), 0) >= MAX_TENTATIVAS:
            form = AuthenticationForm(request)
            return self.render_to_response(self.get_context_data(form=form, bloqueado=True))
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        chave = _chave(self.request)
        try:
            cache.incr(chave)
        except ValueError:
            cache.set(chave, 1, BLOQUEIO_SEGUNDOS)
        return super().form_invalid(form)

    def form_valid(self, form):
        cache.delete(_chave(self.request))
        return super().form_valid(form)


@login_required
def painel(request):
    produtos = Produto.objects.all()
    return render(request, "vitrine/painel.html", {"produtos": produtos})


@login_required
def produto_novo(request):
    form = ProdutoForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Produto salvo com sucesso.")
        return redirect("painel")
    return render(request, "vitrine/produto_form.html", {"form": form, "titulo": "Novo produto"})


@login_required
def produto_editar(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    form = ProdutoForm(request.POST or None, request.FILES or None, instance=produto)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Produto atualizado com sucesso.")
        return redirect("painel")
    return render(request, "vitrine/produto_form.html", {"form": form, "titulo": "Editar produto"})


@login_required
@require_POST
def produto_alternar(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    produto.visivel = not produto.visivel
    produto.save(update_fields=["visivel"])
    estado = "visível na vitrine" if produto.visivel else "oculto da vitrine"
    messages.success(request, f"“{produto.nome}” agora está {estado}.")
    return redirect("painel")


@login_required
@require_POST
def produto_excluir(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    nome = produto.nome
    produto.delete()
    messages.success(request, f"“{nome}” foi excluído.")
    return redirect("painel")


@login_required
def pedidos(request):
    return render(request, "vitrine/painel_pedidos.html", {"pedidos": Pedido.objects.prefetch_related("itens")[:50]})


@login_required
@require_POST
def pedido_status(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    novo = request.POST.get("status")
    if novo in (Pedido.AGUARDANDO, Pedido.PAGO, Pedido.CANCELADO):
        pedido.status = novo
        pedido.save(update_fields=["status"])
        messages.success(request, f"Pedido {pedido.numero} atualizado: {pedido.get_status_display()}.")
    return redirect("pedidos")
