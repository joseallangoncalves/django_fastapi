# Especificação Técnica do Portal Front-end (React + Vite SPA)

Este documento descreve a arquitetura, design visual e a lógica do cliente de integração implementados no portal web front-end desenvolvido em **React** (utilizando **Vite** como build tool), que atua como a interface de usuário Single Page Application (SPA) conectada à API do **FastAPI**.

---

## 1. Separação Física das Camadas (Frontend e Backend)

O sistema foi fisicamente desacoplado para separar o cliente do servidor, facilitando a escalabilidade, manutenção independente e isolamento de processos:

* **Diretório `frontend/` (Frontend Portal - React SPA):** Contém toda a interface SPA em React estruturada de forma modular. Roda por padrão na porta do Vite **`5173`**.
* **Diretório `backend/` (Backend Portal - FastAPI):** Contém o motor de persistência relacional (MySQL ou PostgreSQL), segurança com JWT e criptografia de senhas, além das Agent Skills de IA (Groq). Roda por padrão na porta **`8000`**.

---

## 2. Estrutura de Diretórios do Frontend

A reestruturação da pasta do portal para `frontend/` estabelece a seguinte topologia de arquivos baseada em componentes React:

```text
frontend/
├── package.json                    # Dependências npm e scripts de execução/build
├── vite.config.js                  # Configurações do Vite (incluindo proxy de rotas, se necessário)
├── index.html                      # Ponto de entrada do documento HTML
│
└── src/                            # Diretório de código-fonte React
    ├── main.jsx                    # Ponto de inicialização do React DOM
    ├── App.jsx                     # Componente raiz com configuração de rotas (React Router)
    │
    ├── assets/                     # Recursos de mídia estáticos (imagens, logotipos)
    │
    ├── components/                 # Componentes genéricos e modulares
    │   ├── Button.jsx              # Botões estilizados com efeitos de hover
    │   ├── LoadingOverlay.jsx      # Spinner de carregamento embaçado translúcido
    │   ├── Toast.jsx               # Notificações Toast flutuantes
    │   ├── CodeBlock.jsx           # Caixa preta de terminal com botão de cópia rápida
    │   └── Layout.jsx              # Template de layout (barra lateral, topo e área de conteúdo)
    │
    ├── pages/                      # Páginas e views completas da SPA
    │   ├── Login.jsx               # Tela de Login com formulário e glassmorphism
    │   ├── Register.jsx            # Tela de Cadastro de Usuário
    │   ├── Dashboard.jsx           # Painel principal com cards de métricas e histórico de IA
    │   ├── Storyteller.jsx         # Playground interativo do Agente Storyteller
    │   └── LectureExtractor.jsx    # Playground do Extrator Técnico de Aulas (TEC)
    │
    ├── services/                   # Camada de comunicação de rede
    │   └── api.js                  # Configuração do Axios ou Fetch API com interceptores para injeção de JWT
    │
    └── styles/                     # Estilização global da aplicação
        └── styles.css              # Design System completo (Cosmic Dark Mode, variáveis HSL e efeitos)
```

---

## 3. Integração e Comunicação HTTP (REST API)

A comunicação entre a SPA React e o FastAPI é feita de forma assíncrona utilizando a biblioteca **`axios`** (ou Fetch API padrão) através de chamadas HTTP client-side:

1. **Autenticação Baseada em Token JWT:** Ao efetuar login com sucesso (`POST /auth/login` no FastAPI), a SPA obtém o token de acesso (`access_token`).
2. **Armazenamento Seguro:** O token JWT é mantido no `localStorage` ou `sessionStorage` do navegador, ou guardado em cookies de segurança do cliente.
3. **Injeção de Cabeçalho Bearer:** Através de um interceptor de requisições no Axios (`src/services/api.js`), o token JWT é anexado automaticamente a todas as requisições que exigem autenticação sob o cabeçalho padrão:
   `Authorization: Bearer <token_jwt>`
4. **Tratamento de Expirabilidade (401):** Caso uma requisição retorne `401 Unauthorized`, o cliente React remove o token inválido do armazenamento e redireciona o usuário para a página de login.

---

## 4. Rotas e Páginas da Aplicação (React Router)

### Rotas de Autenticação (Acesso Público/Restrito):
* **`/login` (Página `Login`)**: Formulário de autenticação. Realiza o login na API, salva o token e redireciona o usuário para o dashboard.
* **`/register` (Página `Register`)**: Formulário de criação de conta. Faz as validações no cliente (como igualdade de senhas e tamanho mínimo de 6 caracteres) antes de enviar a requisição de cadastro para a API do FastAPI.

### Rotas Protegidas (Apenas Usuários Autenticados):
* **`/` ou `/dashboard` (Página `Dashboard`)**: Roteia o painel principal do usuário. Busca no FastAPI o histórico de execuções de IA (`GET /contracts/` ou logs) e renderiza as estatísticas em tempo real.
* **`/storyteller` (Página `Storyteller`)**: Interface de input de tema. Envia o payload via API e atualiza o estado com a história gerada pela IA, renderizando-a com formatação de markdown.
* **`/lecture-extractor` (Página `LectureExtractor`)**: Permite colar ou carregar transcrições e exibe o retorno estruturado em formato didático T-E-C (Teoria, Exemplo, Código).

---

## 5. Visual Premium e Design System (`src/styles/styles.css`)

Criamos um **Design System dinâmico e premium** que atende às diretrizes mais rígidas de estética web moderna:

* **Cosmic Dark Theme:** Cores de fundo escuras profundas personalizadas via variáveis de escopo HSL (`--bg-base`, `--bg-surface`, `--bg-card`), evitando pretos e cinzas puros.
* **Acentos de Cor Neon:** Destaques luminosos utilizando tons roxos neons (`--primary`), cianos cibernéticos (`--secondary`) e rosas sintetizadores (`--accent`).
* **Glassmorphism:** Efeito visual de vidro embaçado nas áreas principais (`backdrop-filter: blur(16px)`) com bordas translúcidas sutilmente iluminadas e sombras projetadas profundas.
* **Playgrounds de IA Interativos:**
  * **Visualizadores de Código (`CodeBlock`):** Caixas pretas de terminal para códigos-fonte de fixação com fontes mono-espaçadas premium e um **botão dinâmico "Copiar Código"** que interage com a API de transferência (`navigator.clipboard`) em tempo real com indicador visual de status.
  * **Loading Overlay Dinâmico (`LoadingOverlay`):** Tela de carregamento opaca e embaçada com animação de spinner rotativo exibida em tempo real antes de disparar operações de rede pesadas com a inteligência artificial, informando o status da tarefa.
  * **Toast Alerts (`Toast`):** Alertas flutuantes coloridos que surgem do lado direito da tela para notificar interações bem-sucedidas ou erros de digitação e rede, desaparecendo suavemente após 5 segundos.

