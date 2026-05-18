# Especificação Técnica do Portal Front-end (Django BFF)

Este documento descreve a arquitetura, design visual e a lógica do cliente de integração implementados no portal web front-end desenvolvido em **Django**, que atua como a interface de usuário final e a camada BFF (Backend-for-Frontend) integrada ao motor **FastAPI**.

---

## 1. Separação Física das Camadas (Frontend e Backend)

O sistema foi fisicamente desacoplado para separar o cliente do servidor, facilitando a escalabilidade, manutenção independente e isolamento de processos:

* **Diretório `frontend/` (Frontend Portal - Django):** Contém todas as visualizações, páginas dinâmicas, estilos e a lógica de comunicação BFF. Roda por padrão na porta **`8080`**.
* **Diretório `backend/` (Backend Portal - FastAPI):** Contém o motor de persistência relacional (SQLite), segurança com JWT e criptografia de senhas, além das Agent Skills de IA (Groq). Roda por padrão na porta **`8000`**.

---

## 2. Estrutura de Diretórios do Frontend

A reestruturação e renomeação da pasta do portal para `frontend/` estabeleceu a seguinte topologia de arquivos:

```text
frontend/
├── manage.py                       # Utilitário de gerenciamento e inicialização do Django
│
├── core/                           # Configuração Global e Gateway API
│   ├── settings.py                 # Ativação de apps, caminhos de assets e configurações de sessão
│   ├── urls.py                     # Roteador central (distribui rotas para portal e accounts)
│   ├── wsgi.py / asgi.py           # Adaptadores de servidores web WSGI/ASGI síncronos e assíncronos
│   └── api_client.py               # Gateway/Cliente HTTP que centraliza requisições ao FastAPI
│
├── accounts/                       # Módulo de Login, Cadastro e Controle de Sessão
│   ├── views.py                    # Controllers de login, register e logout síncronos
│   ├── urls.py                     # Rotas de controle de sessão
│   └── apps.py                     # Registro de aplicativo no ecossistema Django
│
├── portal/                         # Módulo dos Painéis Principais e Agent Skills
│   ├── views.py                    # Controllers para Dashboard e chamada de habilidades da IA
│   ├── urls.py                     # Mapeamento do Dashboard e dos playgrounds de IA
│   └── apps.py                     # Registro de aplicativo no ecossistema Django
│
├── templates/                      # Telas HTML Dinâmicas Modernizadas
│   ├── base.html                   # Casca/Layout principal com navegação, toast alerts e loadings
│   ├── accounts/
│   │   ├── login.html              # Tela de Login com formulário e glassmorphism
│   │   └── register.html           # Tela de Cadastro de Usuário
│   └── portal/
│       ├── dashboard.html          # Dashboard com cards de métricas e histórico de consumo de IA
│       ├── storyteller.html        # Playground do Agente Storyteller
│       └── lecture_extractor.html  # Playground do Extrator Técnico de Aulas (Padrão T-E-C)
│
└── static/                         # Recursos Estáticos do Portal
    └── css/
        └── styles.css              # Design System completo (Cosmic Dark Mode, variáveis HSL e efeitos)
```

---

## 3. Integração e Comunicação Híbrida (BFF)

Para garantir segurança e performance, as requisições do Django para o FastAPI são realizadas Server-to-Server utilizando o cliente HTTP síncrono da biblioteca **`httpx`** através de `core/api_client.py`:

1. **Token de Segurança do Sistema (`X-API-Token`):** Todas as requisições geradas pelo Django incluem o cabeçalho HTTP fixo `X-API-Token: 123` para validação interna contra acessos externos maliciosos ao FastAPI.
2. **Sessão JWT Persistente:** Ao efetuar login com sucesso via `POST /auth/login` no FastAPI, o token JWT do usuário (`access_token`) é salvo nos cookies de sessão criptografados do Django (`request.session['access_token']`).
3. **Encaminhamento de Autorização:** Nas requisições subsequentes que exigem nível de usuário (como o histórico de consumo de IA e execução de habilidades), o Django recupera o token da sessão e o injeta como cabeçalho de autenticação Bearer (`Authorization: Bearer <token>`).

---

## 4. Controladores e Lógica do Usuário (BFF Views)

### App: `accounts` (Autenticação)
* **`login_view`**: Valida a presença de dados, consome a API do back-end, salva informações de perfil e o token na sessão e redireciona ao painel principal.
* **`register_view`**: Efetua verificações locais de igualdade de senha e tamanho mínimo (>= 6 caracteres) antes de acionar a persistência segura de criação de conta do FastAPI.
* **`logout_view`**: Solicita a revogação e expiração física do token Bearer no banco e limpa integralmente a sessão no Django.

### App: `portal` (Inteligência Artificial)
* **`auth_required` (Decorator)**: Intercepta e protege todas as rotas do painel, garantindo que usuários não autenticados sejam redirecionados amigavelmente para a tela de login.
* **`dashboard_view`**: Consome o histórico de execuções de IA do usuário autenticado no FastAPI e entrega dados para construção gráfica do painel.
* **`storyteller_view`**: Recebe o tema do formulário e aciona a geração criativa do Llama 3.1 no FastAPI.
* **`lecture_extractor_view`**: Recebe a transcrição textual, invoca o extrator de IA em formato JSON estructurado no FastAPI e retorna os dados mapeados para renderização didática.

---

## 5. Visual Premium e Design System (`static/css/styles.css`)

Criamos um **Design System dinâmico e premium** que atende às diretrizes mais rígidas de estética web moderna:

* **Cosmic Dark Theme:** Cores de fundo escuras profundas personalizadas via variáveis de escopo HSL (`--bg-base`, `--bg-surface`, `--bg-card`), evitando pretos e cinzas puros.
* **Acentos de Cor Neon:** Destaques luminosos utilizando tons roxos neons (`--primary`), cianos cibernéticos (`--secondary`) e rosas sintetizadores (`--accent`).
* **Glassmorphism:** Efeito visual de vidro embaçado nas áreas principais (`backdrop-filter: blur(16px)`) com bordas translúcidas sutilmente iluminadas e sombras projetadas profundas.
* **Playgrounds de IA Interativos:**
  * **Visualizadores de Código:** Caixas pretas de terminal para códigos-fonte de fixação com fontes mono-espaçadas premium e um **botão dinâmico "Copiar Código"** que interage com a API de transferência em tempo real com indicador visual de status.
  * **Loading Overlay Dinâmico:** Uma tela de carregamento opaca embaçada com animação de spinner rotativo é exibida em tempo real antes de disparar operações de rede pesadas com a inteligência artificial, informando o status da tarefa.
  * **Toast Alerts:** Alertas flutuantes coloridos que surgem do lado direito da tela para notificar interações bem-sucedidas ou erros de digitação e rede, desaparecendo suavemente após 5 segundos.
