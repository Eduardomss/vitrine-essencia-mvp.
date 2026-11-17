import django.db.models.deletion
from django.db import migrations, models

import vitrine.models


class Migration(migrations.Migration):

    dependencies = [
        ("vitrine", "0002_produto_categoria"),
    ]

    operations = [
        migrations.CreateModel(
            name="Pedido",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("codigo", models.CharField(default=vitrine.models.gerar_codigo, editable=False, max_length=16, unique=True)),
                ("total", models.DecimalField(decimal_places=2, max_digits=10, verbose_name="Total (R$)")),
                (
                    "status",
                    models.CharField(
                        choices=[("aguardando", "Aguardando pagamento"), ("pago", "Pago"), ("cancelado", "Cancelado")],
                        default="aguardando",
                        max_length=12,
                    ),
                ),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "pedido",
                "verbose_name_plural": "pedidos",
                "ordering": ["-criado_em", "-id"],
            },
        ),
        migrations.CreateModel(
            name="ItemPedido",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=100)),
                ("preco", models.DecimalField(decimal_places=2, max_digits=8)),
                ("qtd", models.PositiveSmallIntegerField()),
                (
                    "pedido",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="itens", to="vitrine.pedido"
                    ),
                ),
            ],
        ),
    ]
