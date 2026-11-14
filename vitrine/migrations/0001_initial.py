import django.core.validators
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Produto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=100, verbose_name="Nome do produto")),
                ("descricao", models.TextField(blank=True, max_length=500, verbose_name="Descrição")),
                (
                    "preco",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=8,
                        validators=[
                            django.core.validators.MinValueValidator(
                                Decimal("0.01"), message="O preço deve ser maior que zero."
                            )
                        ],
                        verbose_name="Preço (R$)",
                    ),
                ),
                ("foto", models.ImageField(blank=True, upload_to="produtos/", verbose_name="Foto")),
                ("visivel", models.BooleanField(default=True, verbose_name="Mostrar na vitrine")),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "produto",
                "verbose_name_plural": "produtos",
                "ordering": ["-criado_em", "-id"],
            },
        ),
    ]
