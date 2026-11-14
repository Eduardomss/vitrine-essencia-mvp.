# Vitrine Essência (MVP)

Vitrine online simples, com pedido pelo WhatsApp, para uma pequena loja de produtos naturais e artesanais (Z&D Essência Natural, Guarulhos/SP).

Projeto da disciplina de Projeto de Software (Experiência Prática), do curso de Análise e Desenvolvimento de Sistemas. O MVP já tem vitrine, pedido pelo WhatsApp, login e painel de produtos.

## Problema

A loja parceira vende quase só por um marketplace, cujas taxas reduzem bastante a margem de cada venda, e as vendas variam conforme a visibilidade na plataforma. A proprietária não tem verba para anúncios nem para uma loja virtual completa.

## Solução (MVP)

Uma página web própria, leve e de custo muito baixo, em que o cliente vê os produtos e faz o pedido pelo WhatsApp com a mensagem já preenchida. A proprietária gerencia os produtos por um painel protegido por login, pelo celular ou pelo computador.

Contribui com o **ODS 8 – Trabalho decente e crescimento econômico**, ao apoiar um pequeno negócio local.

## Funcionalidades planejadas

| Código | Requisito | Prioridade |
|--------|-----------|------------|
| RF01 | Vitrine pública com os produtos visíveis | Obrigatório |
| RF02 | Pedido pelo WhatsApp com mensagem pré-preenchida | Obrigatório |
| RF03 | Login da proprietária no painel | Obrigatório |
| RF04 | Cadastro de produto | Obrigatório |
| RF05 | Edição de produto | Obrigatório |
| RF06 | Ocultar ou excluir produto | Desejável |
| RF07 | Link e QR Code da vitrine | Desejável |

## Tecnologias

- Python 3.12
- Django 5.2 LTS (rotas, templates, login, formulários e testes)
- HTML e CSS próprios, responsivos e acessíveis (contraste, áreas de toque de 44 px, foco visível)
- Pillow (validação e redução das fotos)
- SQLite (banco embarcado)

## Arquitetura

Aplicação monolítica em camadas: apresentação (templates), regras de negócio (views e serviços) e acesso a dados (modelos do Django).

## Como executar localmente

```bash
# 1. Criar e ativar o ambiente virtual
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 2. Instalar as dependências
pip install -r requirements.txt

# 3. Criar o banco de dados e a conta da proprietária
python manage.py migrate
python manage.py createsuperuser

# 4. Iniciar o servidor
python manage.py runserver
```

Depois, abra http://127.0.0.1:8000/ no navegador. A vitrine fica em `/` e a área da proprietária em `/entrar/`.

### Variáveis de ambiente (opcionais em desenvolvimento)

| Variável | Para que serve |
|----------|----------------|
| `DJANGO_SECRET_KEY` | Chave secreta (obrigatória quando `DJANGO_DEBUG=0`) |
| `DJANGO_DEBUG` | `1` (padrão) ou `0` em produção |
| `DJANGO_ALLOWED_HOSTS` | Domínios permitidos, separados por vírgula |
| `WHATSAPP_NUMERO` | Número da loja com país e DDD, só dígitos (ex.: `5511999999999`) |
| `LOJA_NOME` | Nome exibido no site |

## Testes

```bash
python manage.py test
```

Os testes cobrem a vitrine, a mensagem do WhatsApp, o login com bloqueio, o cadastro/edição de produtos e a validação de fotos.

## Segurança

- Senhas guardadas apenas como hash (mecanismo nativo do Django).
- Painel protegido por login e token CSRF.
- Login bloqueado por 15 minutos após 5 tentativas erradas.
- Upload de foto validado com Pillow (só imagens) e reduzido a no máximo 1000 px.
- Chave secreta e demais segredos em variáveis de ambiente, fora do repositório.
- Não são coletados dados pessoais dos clientes.

## Status

- [x] Planejamento, requisitos e protótipo das telas
- [x] Estrutura do projeto Django
- [x] Vitrine e pedido pelo WhatsApp
- [x] Painel com login e cadastro de produtos
- [x] Testes automatizados
- [ ] Publicação (PythonAnywhere)
