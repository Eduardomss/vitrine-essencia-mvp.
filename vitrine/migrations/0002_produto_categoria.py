from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vitrine", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="produto",
            name="categoria",
            field=models.CharField(
                choices=[
                    ("natal", "Natal"),
                    ("sabonetes", "Sabonetes"),
                    ("pomadas", "Pomadas"),
                    ("presentes", "Presentes"),
                    ("outros", "Outros"),
                ],
                default="outros",
                max_length=20,
                verbose_name="Categoria",
            ),
        ),
    ]
