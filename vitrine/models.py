from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from PIL import Image

LIMITE_LADO_FOTO = 1000  # px; fotos maiores são reduzidas ao salvar


class Produto(models.Model):
    nome = models.CharField("Nome do produto", max_length=100)
    descricao = models.TextField("Descrição", max_length=500, blank=True)
    preco = models.DecimalField(
        "Preço (R$)",
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"), message="O preço deve ser maior que zero.")],
    )
    foto = models.ImageField("Foto", upload_to="produtos/", blank=True)
    visivel = models.BooleanField("Mostrar na vitrine", default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em", "-id"]
        verbose_name = "produto"
        verbose_name_plural = "produtos"

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.foto:
            self._reduzir_foto()

    def _reduzir_foto(self):
        """Reduz fotos grandes para economizar espaço e acelerar a vitrine."""
        try:
            with Image.open(self.foto.path) as img:
                img.load()
                formato = img.format
                copia = img.copy()
            if max(copia.size) <= LIMITE_LADO_FOTO:
                return
            copia.thumbnail((LIMITE_LADO_FOTO, LIMITE_LADO_FOTO))
            copia.save(self.foto.path, format=formato, optimize=True)
        except (OSError, ValueError):
            # Se não for possível reduzir, a foto original continua válida.
            pass
