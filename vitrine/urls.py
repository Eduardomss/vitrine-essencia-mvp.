from django.urls import path

from . import views

urlpatterns = [
    path("", views.vitrine, name="vitrine"),
    path("pedido/<int:pk>/", views.pedido, name="pedido"),
]
