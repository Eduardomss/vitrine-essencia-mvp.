from django import forms
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile

from .models import Produto

TAMANHO_MAX_FOTO = 5 * 1024 * 1024  # 5 MB
LIMITE_PIXELS = 25_000_000  # evita imagens enormes que esgotam a memória ao serem reduzidas


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ["nome", "descricao", "preco", "foto", "visivel"]
        localized_fields = ["preco"]  # aceita "25,90"
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 3}),
            "preco": forms.TextInput(attrs={"inputmode": "decimal"}),
        }
        help_texts = {
            "preco": "Digite só números. Exemplo: 25,90",
            "foto": "Opcional. Imagem JPG ou PNG de até 5 MB.",
        }
        error_messages = {
            "nome": {"required": "Informe o nome do produto."},
            "preco": {
                "required": "Informe o preço do produto.",
                "invalid": "Digite o preço só com números. Exemplo: 25,90",
            },
        }

    def clean_foto(self):
        foto = self.cleaned_data.get("foto")
        if isinstance(foto, UploadedFile) and foto.size > TAMANHO_MAX_FOTO:
            raise ValidationError("A foto é muito grande. Envie uma imagem de até 5 MB.")
        imagem = getattr(foto, "image", None)  # objeto Pillow criado na validação do ImageField
        if imagem is not None:
            largura, altura = imagem.size
            if largura * altura > LIMITE_PIXELS:
                raise ValidationError("A imagem tem dimensões grandes demais. Reduza a foto e tente de novo.")
        return foto
