from django.contrib.auth.views import LogoutView
from django.urls import path

from . import painel, views

urlpatterns = [
    path("", views.vitrine, name="vitrine"),
    path("manifest.webmanifest", views.manifest, name="manifest"),
    path("sw.js", views.service_worker, name="service_worker"),
    path("pedido/<int:pk>/", views.pedido, name="pedido"),
    path("entrar/", painel.LoginComBloqueio.as_view(), name="login"),
    path("sair/", LogoutView.as_view(), name="logout"),
    path("painel/", painel.painel, name="painel"),
    path("painel/novo/", painel.produto_novo, name="produto_novo"),
    path("painel/<int:pk>/editar/", painel.produto_editar, name="produto_editar"),
    path("painel/<int:pk>/alternar/", painel.produto_alternar, name="produto_alternar"),
    path("painel/<int:pk>/excluir/", painel.produto_excluir, name="produto_excluir"),
]
