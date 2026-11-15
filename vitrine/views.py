from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.templatetags.static import static

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
const EXCLUIDOS = ['/painel', '/entrar', '/sair', '/admin'];

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
