from django.conf import settings


def loja(request):
    """Disponibiliza o nome da loja em todos os templates."""
    return {"LOJA_NOME": settings.LOJA_NOME}
