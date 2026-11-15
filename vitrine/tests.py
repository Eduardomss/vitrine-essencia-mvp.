import shutil
import tempfile
from decimal import Decimal
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from . import servicos
from .models import Produto

MEDIA_TESTE = tempfile.mkdtemp()


def imagem_bytes(tamanho=(10, 10), formato="PNG"):
    buf = BytesIO()
    Image.new("RGB", tamanho, "green").save(buf, format=formato)
    return buf.getvalue()


class AppInstalavelTests(TestCase):
    def test_manifesto_tem_nome_e_icones(self):
        resp = self.client.get(reverse("manifest"))
        self.assertEqual(resp.status_code, 200)
        dados = resp.json()
        self.assertEqual(dados["display"], "standalone")
        self.assertEqual(len(dados["icons"]), 2)

    def test_service_worker_e_javascript(self):
        resp = self.client.get(reverse("service_worker"))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("javascript", resp["Content-Type"])


class VitrineTests(TestCase):
    def setUp(self):
        self.visivel = Produto.objects.create(nome="Pomada Energética", preco=Decimal("51.00"))
        self.oculto = Produto.objects.create(nome="Produto Escondido", preco=Decimal("10.00"), visivel=False)

    def test_vitrine_mostra_apenas_produtos_visiveis(self):
        resp = self.client.get(reverse("vitrine"))
        self.assertContains(resp, "Pomada Energética")
        self.assertNotContains(resp, "Produto Escondido")

    def test_vitrine_vazia_mostra_aviso(self):
        Produto.objects.all().delete()
        resp = self.client.get(reverse("vitrine"))
        self.assertContains(resp, "Nenhum produto disponível")

    def test_pedido_de_produto_oculto_retorna_404(self):
        resp = self.client.get(reverse("pedido", args=[self.oculto.pk]))
        self.assertEqual(resp.status_code, 404)


@override_settings(WHATSAPP_NUMERO="5511999999999")
class PedidoWhatsAppTests(TestCase):
    def setUp(self):
        self.produto = Produto.objects.create(nome="Pomada Energética", preco=Decimal("51.00"))

    def test_mensagem_tem_quantidade_nome_e_total(self):
        msg = servicos.montar_mensagem(self.produto, 2)
        self.assertIn("2x Pomada Energética", msg)
        self.assertIn("Total: R$ 102,00", msg)

    def test_link_usa_numero_da_loja(self):
        link = servicos.montar_link_whatsapp(self.produto, 1)
        self.assertTrue(link.startswith("https://wa.me/5511999999999?text="))

    def test_quantidade_invalida_vira_um(self):
        for texto in ["abc", "", "0", "-3", None]:
            self.assertEqual(servicos.limpar_quantidade(texto), 1)

    def test_quantidade_acima_do_limite_vira_99(self):
        self.assertEqual(servicos.limpar_quantidade("500"), 99)

    def test_tela_de_pedido_calcula_total(self):
        resp = self.client.get(reverse("pedido", args=[self.produto.pk]), {"qtd": "3"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Total: R$ 153,00")


@override_settings(MEDIA_ROOT=MEDIA_TESTE)
class PainelTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_TESTE, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.usuario = get_user_model().objects.create_user("dulce", password="senha-forte-123")

    def entrar(self):
        self.client.login(username="dulce", password="senha-forte-123")

    def test_painel_exige_login(self):
        resp = self.client.get(reverse("painel"))
        self.assertRedirects(resp, "/entrar/?next=/painel/")

    def test_cadastro_exige_login(self):
        resp = self.client.post(reverse("produto_novo"), {"nome": "X", "preco": "10"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Produto.objects.count(), 0)

    def test_cadastra_produto(self):
        self.entrar()
        resp = self.client.post(
            reverse("produto_novo"),
            {"nome": "Sabonete", "descricao": "Natural", "preco": "15.90", "visivel": "on"},
        )
        self.assertRedirects(resp, reverse("painel"))
        self.assertEqual(Produto.objects.get().preco, Decimal("15.90"))

    def test_preco_zero_e_rejeitado(self):
        self.entrar()
        resp = self.client.post(reverse("produto_novo"), {"nome": "Sabonete", "preco": "0"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "O preço deve ser maior que zero.")
        self.assertEqual(Produto.objects.count(), 0)

    def test_nome_obrigatorio(self):
        self.entrar()
        resp = self.client.post(reverse("produto_novo"), {"nome": "", "preco": "10"})
        self.assertContains(resp, "Informe o nome do produto.")

    def test_edita_produto(self):
        self.entrar()
        p = Produto.objects.create(nome="Velho", preco=Decimal("5.00"))
        self.client.post(reverse("produto_editar", args=[p.pk]), {"nome": "Novo", "preco": "7.50", "visivel": "on"})
        p.refresh_from_db()
        self.assertEqual((p.nome, p.preco), ("Novo", Decimal("7.50")))

    def test_ocultar_produto_tira_da_vitrine(self):
        self.entrar()
        p = Produto.objects.create(nome="Pomada", preco=Decimal("5.00"))
        self.client.post(reverse("produto_alternar", args=[p.pk]))
        p.refresh_from_db()
        self.assertFalse(p.visivel)
        resp = self.client.get(reverse("vitrine"))
        self.assertNotIn(p, resp.context["produtos"])  # o aviso de sucesso também cita o nome

    def test_excluir_exige_post(self):
        self.entrar()
        p = Produto.objects.create(nome="Pomada", preco=Decimal("5.00"))
        self.assertEqual(self.client.get(reverse("produto_excluir", args=[p.pk])).status_code, 405)
        self.client.post(reverse("produto_excluir", args=[p.pk]))
        self.assertEqual(Produto.objects.count(), 0)

    def test_arquivo_que_nao_e_imagem_e_rejeitado(self):
        self.entrar()
        falso = SimpleUploadedFile("foto.jpg", b"isto nao e imagem", content_type="image/jpeg")
        resp = self.client.post(reverse("produto_novo"), {"nome": "X", "preco": "10", "foto": falso})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Produto.objects.count(), 0)

    def test_foto_grande_e_reduzida(self):
        self.entrar()
        arq = SimpleUploadedFile("grande.png", imagem_bytes((2400, 1800)), content_type="image/png")
        self.client.post(reverse("produto_novo"), {"nome": "X", "preco": "10", "foto": arq})
        p = Produto.objects.get()
        with Image.open(p.foto.path) as img:
            self.assertLessEqual(max(img.size), 1000)


class LoginBloqueioTests(TestCase):
    def setUp(self):
        cache.clear()
        get_user_model().objects.create_user("dulce", password="senha-forte-123")

    def test_bloqueia_apos_cinco_tentativas_erradas(self):
        for _ in range(5):
            self.client.post(reverse("login"), {"username": "dulce", "password": "errada"})
        resp = self.client.post(reverse("login"), {"username": "dulce", "password": "senha-forte-123"})
        self.assertContains(resp, "Muitas tentativas")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_correto_funciona(self):
        resp = self.client.post(reverse("login"), {"username": "dulce", "password": "senha-forte-123"})
        self.assertRedirects(resp, reverse("painel"), fetch_redirect_response=False)
