# Portal Híbrido: Django + FastAPI com Habilidades de Inteligência Artificial (Agent Skills)

Este repositório contém uma aplicação híbrida de alta performance e visual premium que integra um portal web desenvolvido em **Django** (Frontend/BFF) a um motor de APIs robusto desenvolvido em **FastAPI** (Backend/IA) com integração ao LLM Llama 3.1 da API Groq Cloud.

---

## 🚀 Como Executar o Sistema pelo Terminal

Há duas maneiras de inicializar os servidores: de forma automática (usando o script utilitário em PowerShell) ou manualmente em abas separadas do seu terminal.

### Método 1: Inicialização Automática (Recomendado)

Criamos um script utilitário em PowerShell na raiz do projeto que abre duas novas janelas de comando e inicia ambos os servidores de forma simultânea.

1. Abra um terminal do PowerShell na raiz do projeto (`django_fastapi`).
2. Execute o seguinte comando:
   ```powershell
   .\run_servers.ps1
   ```
3. O script irá:
   * Inicializar o FastAPI na porta `8000`.
   * Inicializar o Django na porta `8080`.
   * As telas permanecerão abertas em novas janelas do terminal para facilitar o acompanhamento dos logs de rede em tempo real.

---

### Método 2: Inicialização Manual (Passo a Passo)

Caso prefira rodar ou gerenciar cada servidor individualmente, abra duas abas ou janelas distintas do terminal na raiz do projeto:

#### Passo 1: Iniciar o Backend (FastAPI)
1. No terminal 1, navegue para o diretório do backend:
   ```bash
   cd backend
   ```
2. Inicie o servidor FastAPI utilizando o gerenciador `uv`:
   ```bash
   uv run uvicorn main:app --port 8000 --reload
   ```
   *(O servidor backend estará ouvindo no endereço `http://127.0.0.1:8000`)*.

#### Passo 2: Iniciar o Frontend (Django)
1. No terminal 2, navegue para o diretório do frontend:
   ```bash
   cd frontend
   ```
2. Inicie o servidor Django utilizando o gerenciador `uv`:
   ```bash
   uv run python manage.py runserver 8080
   ```
   *(O portal frontend estará ouvindo no endereço `http://127.0.0.1:8080`)*.

---

## 🔑 Credenciais Padrão de Acesso

Para acessar o portal e testar todas as Habilidades de IA imediatamente, utilize o usuário administrador padrão que é semeado automaticamente na inicialização do servidor:

* **E-mail / Login:** `admin@admin.com`
* **Senha:** `admin`

*Nota: Você também pode usar o botão "Criar uma conta" na tela de login para cadastrar novos usuários dinamicamente.*

---

## 🔗 Links e Portas de Acesso

Com os servidores rodando, você pode acessar:

* **Portal Frontend (Django):** [http://127.0.0.1:8080](http://127.0.0.1:8080)
  * Interface visual com tema escuro (Cosmic Dark), autenticação de usuários, logs de consumo e painéis (Playgrounds) de Inteligência Artificial para geração de histórias e extração estruturada de conteúdo técnico de aulas.
* **Documentação das APIs (FastAPI - Swagger):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
  * Swagger interativo com todos os endpoints CRUD de usuários, autenticação JWT, histórico de execução e as Agent Skills integradas ao Groq Cloud.

---

## 📂 Estrutura de Pastas

* `frontend/`: Todo o código da interface visual dinâmica, views BFF Django, formulários, templates HTML e folhas de estilos CSS.
* `backend/`: Código de negócio síncrono da API, conexão ORM SQLAlchemy com o banco SQLite local (`pos_sistema.db`), schemas de validação Pydantic.
* `.agents/`: Especificações de comportamento declarativas dos agentes autônomos (pasta `skills/` contendo as 15 habilidades descritas em formato `SKILL.md`).
* `agents/`: Camada de código executável que gerencia a engenharia de prompts e as chamadas para a API do Groq Cloud.
* `spec/`: Documentos de planejamento e especificação técnica das camadas.