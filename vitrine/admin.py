from django.contrib import admin

from .models import Produto


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("nome", "preco", "visivel", "criado_em")
    list_filter = ("visivel",)
    search_fields = ("nome",)
