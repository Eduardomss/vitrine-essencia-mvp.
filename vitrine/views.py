from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.templatetags.static import static
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from . import servicos
from .models import CATEGORIAS, Pedido, Produto


def vitrine(request):
    """Vitrine pública: lista apenas os produtos marcados como visíveis (RF01)."""
    base = Produto.objects.filter(visivel=True)
    busca = request.GET.get("q", "").strip()
    cat = request.GET.get("cat", "")
    produtos = base
    if cat in dict(CATEGORIAS):
        produtos = produtos.filter(categoria=cat)
    else:
        cat = ""
    if busca:
        produtos = produtos.filter(Q(nome__icontains=busca) | Q(descricao__icontains=busca))

    contagem = dict(base.order_by().values_list("categoria").annotate(n=Count("id")))
    abas = [{"chave": "", "nome": "Todos", "n": base.count()}]
    abas += [{"chave": k, "nome": nome, "n": contagem[k]} for k, nome in CATEGORIAS if contagem.get(k)]

    carrinho = request.session.get("carrinho", {})
    produtos = list(produtos)
    for p in produtos:
        p.qtd_pedido = int(carrinho.get(str(p.pk), 0))
    contexto = {
        "produtos": produtos,
        "abas": abas,
        "cat": cat,
        "busca": busca,
        "proximo": request.get_full_path(),
        "tem_base": base.exists(),
    }
    return render(request, "vitrine/lista.html", contexto)


def _destino_seguro(request, padrao="vitrine"):
    destino = request.POST.get("next", "")
    if destino and url_has_allowed_host_and_scheme(destino, allowed_hosts={request.get_host()}):
        return destino
    return reverse(padrao)


@require_POST
def carrinho_alterar(request, pk):
    """Adiciona, soma, diminui ou remove um produto do pedido (guardado na sessão)."""
    produto = get_object_or_404(Produto, pk=pk, visivel=True)
    acao = request.POST.get("acao", "inc")
    carrinho = request.session.get("carrinho", {})
    if acao == "remover":
        carrinho = servicos.adicionar(carrinho, produto.pk, -servicos.QTD_MAX)
    elif acao == "dec":
        carrinho = servicos.adicionar(carrinho, produto.pk, -1)
    else:
        carrinho = servicos.adicionar(carrinho, produto.pk, 1)
    request.session["carrinho"] = carrinho
    destino = _destino_seguro(request)
    if "#" not in destino and request.POST.get("ancora"):
        destino += "#produto-" + str(produto.pk)
    return redirect(destino)


def carrinho(request):
    """Tela do pedido com todos os produtos escolhidos e o botão do WhatsApp."""
    itens = servicos.itens_do_carrinho(request.session.get("carrinho", {}))
    contexto = {
        "itens": itens,
        "total": servicos.formatar_reais(servicos.total_dos_itens(itens)),
        "link_whatsapp": servicos.montar_link_carrinho(itens) if itens else "",
    }
    return render(request, "vitrine/carrinho.html", contexto)


@require_POST
def finalizar(request):
    """Transforma o carrinho em um pedido com link próprio e vai para a tela de pagamento."""
    itens = servicos.itens_do_carrinho(request.session.get("carrinho", {}))
    if not itens:
        messages.error(request, "Seu pedido está vazio. Escolha ao menos um produto.")
        return redirect("carrinho")
    pedido = servicos.criar_pedido(itens)
    request.session["carrinho"] = {}
    return redirect("pedido_final", codigo=pedido.codigo)


def pedido_final(request, codigo):
    """Resumo do pedido: pagar por Pix e enviar o link do pedido pelo WhatsApp."""
    pedido = get_object_or_404(Pedido, codigo=codigo)
    link = request.build_absolute_uri(request.path)
    contexto = {
        "pedido": pedido,
        "itens": pedido.itens.all(),
        "pix": servicos.pix_do_pedido(pedido) if pedido.status == Pedido.AGUARDANDO else None,
        "pix_chave": settings.PIX_CHAVE,
        "link_whatsapp": servicos.montar_link_pedido_whatsapp(pedido, link),
    }
    return render(request, "vitrine/pedido_final.html", contexto)


def como_pedir(request):
    return render(request, "vitrine/como_pedir.html")


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


def manifest(request):
    """Manifesto do aplicativo: permite instalar a vitrine na tela inicial do celular."""
    dados = {
        "name": settings.LOJA_NOME,
        "short_name": "Z&D Essência",
        "description": "Vitrine online com pedido pelo WhatsApp",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "background_color": "#FFF8EE",
        "theme_color": "#2F6B3F",
        "lang": "pt-BR",
        "icons": [
            {"src": static("vitrine/icon-192.png"), "sizes": "192x192", "type": "image/png"},
            {"src": static("vitrine/icon-512.png"), "sizes": "512x512", "type": "image/png"},
        ],
    }
    return JsonResponse(dados, content_type="application/manifest+json")


SERVICE_WORKER = """
const CACHE = 'vitrine-v1';
const EXCLUIDOS = ['/painel', '/entrar', '/sair', '/admin', '/carrinho', '/finalizar', '/meu-pedido'];

self.addEventListener('install', (e) => self.skipWaiting());
self.addEventListener('activate', (e) => e.waitUntil(self.clients.claim()));

self.addEventListener('fetch', (e) => {
  const req = e.request;
  const url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== location.origin) return;
  if (EXCLUIDOS.some((p) => url.pathname.startsWith(p))) return;
  e.respondWith(
    fetch(req)
      .then((res) => {
        const copia = res.clone();
        caches.open(CACHE).then((c) => c.put(req, copia));
        return res;
      })
      .catch(() => caches.match(req))
  );
});
"""


def service_worker(request):
    """Service worker na raiz do site: guarda a vitrine para abrir mesmo com internet instável."""
    resp = HttpResponse(SERVICE_WORKER, content_type="application/javascript")
    resp["Cache-Control"] = "no-cache"
    return resp
