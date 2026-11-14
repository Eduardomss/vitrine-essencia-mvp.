# Vitrine Essência (MVP)

Vitrine online simples, com pedido pelo WhatsApp, para uma pequena loja de produtos naturais e artesanais (Z&D Essência Natural, Guarulhos/SP).

Projeto da disciplina de Projeto de Software (Experiência Prática), do curso de Análise e Desenvolvimento de Sistemas. Está **em desenvolvimento**.

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
- Bootstrap 5 (interface responsiva, servido junto com a aplicação)
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

Depois, abra http://127.0.0.1:8000/ no navegador.

> Os arquivos de código serão adicionados conforme o desenvolvimento avança.

## Segurança

- Senhas guardadas apenas como hash (mecanismo nativo do Django).
- Painel protegido por login e token CSRF.
- Chave secreta e demais segredos em variáveis de ambiente, fora do repositório.
- Não são coletados dados pessoais dos clientes.

## Status

- [x] Planejamento, requisitos e protótipo das telas
- [ ] Estrutura do projeto Django
- [ ] Vitrine e pedido pelo WhatsApp
- [ ] Painel com login e cadastro de produtos
- [ ] Testes e publicação
