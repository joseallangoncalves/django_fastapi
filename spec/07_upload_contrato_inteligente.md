# Especificação Técnica: Upload de Contrato e Extração de Dados Inteligentes (IA)

Este documento especifica a arquitetura, o fluxo de dados, os schemas e os endpoints para a nova funcionalidade de **Upload e Processamento Inteligente de Contratos** integrada ao ecossistema React/FastAPI com suporte a IA autônoma via Groq.

---

## 1. Visão Geral do Fluxo (Roteamento Inteligente)

A funcionalidade permitirá ao usuário carregar qualquer arquivo nos formatos **PDF, DOC/DOCX, TXT ou Markdown (`.md`)** através de uma interface amigável. Em vez de assumir que é um contrato, o sistema passa o documento por um **Classificador Inteligente** (Agente Classifier), que analisa as características do texto contra as 15 Habilidades disponíveis em `.agents/skills/` e executa dinamicamente a Habilidade mais recomendada, persistindo os dados e os registrando no banco de dados MySQL ou PostgreSQL de forma unificada.

```text
[Usuário] ---> (Envia arquivo/documento) ---> [Portal React (Front)]
                                                   │
                                            (Envia via multipart/form-data)
                                                   ▼
                                              [FastAPI (Back)]
                                                   │
                                      (Lê e extrai texto do documento)
                                                   ▼
                                        [Agente Classifier (Groq)]
                                                   │
                                      (Roteia e Executa Skill Ótima)
                                                   ▼
                                          [Banco de Dados MySQL/PostgreSQL]
                                                   │
                                      (Persiste dados e histórico)
                                                   ▼
                                          [Dashboard atualizado]
```

---

## 2. Dados a Serem Extraídos do Contrato

O agente autônomo de IA lerá o texto bruto do contrato e estruturará os seguintes metadados obrigatórios:

1. **Número do Contrato:** Identificador ou código do contrato (ex: `CT-2026-9812`).
2. **Contratante:** Nome da entidade/empresa contratante.
3. **Contratado:** Nome da entidade/empresa prestadora de serviços.
4. **Data de Início:** Data em formato ISO (`AAAA-MM-DD`).
5. **Data de Término:** Data de encerramento do contrato em formato ISO (`AAAA-MM-DD`).
6. **Valor Total:** Valor total do contrato no formato monetário numérico (ex: `150000.00`).
7. **Moeda:** Moeda do contrato (ex: `BRL`, `USD`).
8. **Resumo Executivo:** Um breve resumo de 2 a 3 frases descrevendo o objeto principal do contrato.

---

## 3. Estrutura do Banco de Dados (FastAPI Models)

Para armazenar estes metadados, adicionaremos a entidade **`Contrato`** no banco de dados.

### Nova Tabela: `contratos`
```python
# backend/models/contrato.py
from datetime import datetime
from sqlalchemy import Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from db.connection import Base

class Contrato(Base):
    __tablename__ = "contratos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"), nullable=True)
    numero_contrato: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    contratante: Mapped[str] = mapped_column(String(100), nullable=False)
    contratado: Mapped[str] = mapped_column(String(100), nullable=False)
    data_inicio: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    data_fim: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    valor_total: Mapped[float] = mapped_column(Float, nullable=False)
    moeda: Mapped[str] = mapped_column(String(10), default="BRL", nullable=False)
    resumo: Mapped[str] = mapped_column(Text, nullable=True)
    observacoes: Mapped[str] = mapped_column(Text, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
```

---

## 4. Schemas de Validação (Pydantic DTOs)

Definiremos as estruturas de validação de dados para garantir o formato correto no backend:

```python
# backend/schemas/contrato.py
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class ContratoBase(BaseModel):
    numero_contrato: str = Field(..., description="Número identificador do contrato")
    contratante: str = Field(..., description="Razão Social ou Nome do Contratante")
    contratado: str = Field(..., description="Razão Social ou Nome do Contratado")
    data_inicio: date = Field(..., description="Data de início do contrato")
    data_fim: date = Field(..., description="Data de término do contrato")
    valor_total: float = Field(..., description="Valor total em formato flutuante")
    moeda: str = Field("BRL", description="Moeda sob a qual o contrato foi regido")
    resumo: Optional[str] = Field(None, description="Resumo do objeto contratual gerado pela IA")
    observacoes: Optional[str] = Field(None, description="Observações ou anotações manuais adicionadas ao contrato")

class ContratoCreate(BaseModel):
    numero_contrato: str
    contratante: str
    contratado: str
    data_inicio: date
    data_fim: date
    valor_total: float
    moeda: str = "BRL"
    resumo: Optional[str] = None
    observacoes: Optional[str] = None

class ContratoUpdate(BaseModel):
    numero_contrato: Optional[str] = None
    contratante: Optional[str] = None
    contratado: Optional[str] = None
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    valor_total: Optional[float] = None
    moeda: Optional[str] = None
    resumo: Optional[str] = None
    observacoes: Optional[str] = None

class ContratoOutput(ContratoBase):
    id: int
    criado_em: str

    class Config:
        from_attributes = True
```

---

## 5. Agente de Classificação e Roteamento Dinâmico (`backend/agents/classifier.py`)

Esta camada carrega de forma dinâmica as especificações das 15 Habilidades de Agente declaradas em `.agents/skills/[nome]/SKILL.md`, usando o LLM da Groq como um roteador de arquivos inteligente para classificar o texto carregado e aplicar a melhor habilidade disponível:

```python
# backend/agents/classifier.py
import os
import re
import json
from agents.base import client

def classificar_e_rotear_documento(texto_documento: str) -> dict:
    # 1. Carrega dinamicamente a definição das 15 habilidades em `.agents/skills/`
    # 2. Constrói um prompt inteligente listando as habilidades
    # 3. Invoca o modelo `llama-3.1-8b-instant` para classificar o documento e obter recomendação em JSON
    # 4. Retorna a recomendação (skill recomendada, justificativa, flag e_contrato, plano de ação)
```

---

## 6. Endpoints do Backend (FastAPI)

Adicionaremos um novo router `backend/routers/contracts.py` protegendo os seguintes endpoints:

* **`POST /contracts/upload`**: Recebe o arquivo/documento via `UploadFile` contendo suporte a múltiplos formatos de arquivo (.pdf, .docx, .doc, .txt, .md):
  * **Tratamento de Arquivos e Limite de Tokens**: Se o texto extraído exceder 12.000 caracteres, ele é truncado mantendo o início e o fim (primeiros 9.000 e últimos 3.000 caracteres) para respeitar rigorosamente os limites de TPM da API do Groq Cloud.
  * **Classificação e Roteamento**: O endpoint aciona o Agente Classifier (`classificar_e_rotear_documento`) para verificar a qual das 15 habilidades do `.agents/skills/` o texto pertence.
  * **Execução Dinâmica**: Se for um contrato, executa a habilidade `skill_extrair_contrato` estruturando os metadados completos. Caso contrário, executa dinamicamente a Habilidade correspondente carregando as diretrizes de seu `SKILL.md` (como o de `resumo`, `analisador-whatsapp`, etc.), persistindo de forma adaptada no banco de dados MySQL/PostgreSQL e gravando a justificativa detalhada e o log no histórico de execução.
* **`GET /contracts/`**: Lista todos os registros analisados e persistidos do usuário autenticado.
* **`GET /contracts/{contract_id}`**: Visualiza em detalhe um contrato específico pelo ID, garantindo que o contrato pertença ao usuário autenticado.
* **`PUT /contracts/{contract_id}`**: Permite a edição/atualização manual das informações do contrato (ex: ajustar um valor ou data extraída incorretamente).
* **`DELETE /contracts/{contract_id}`**: Exclui fisicamente do banco de dados o contrato especificado, liberando espaço e atualizando as estatísticas do painel. Esta rota é ativada via front-end pelos botões "Excluir Registro" nas interfaces de detalhes e lista de contratos, efetuando a exclusão em cascata.

---

## 7. Integração com Frontend (React)

* **Interface Visual**: Criaremos um componente React com formulário de upload de arquivos com área *Drag and Drop* (arrastar e soltar), aceitando explicitamente as extensões `.pdf`, `.doc`, `.docx`, `.txt` e `.md` (estilizado em CSS moderno e animado).
* **Painel de Resultados**: Uma exibição em estilo de cartões interativos mostrando os detalhes extraídos (Número, Contratante, Contratado, Datas, Valor e o Resumo da IA).
* **Persistência**: Uma chamada assíncrona multipart (utilizando Axios ou Fetch API) do React para o FastAPI transmitindo o arquivo carregado de forma transparente.

---

## 8. Dependências de Sistema e Execução

### A. Dependências de Processamento de Arquivos
Para que a leitura e a extração automatizada de textos a partir de formatos ricos funcionem perfeitamente, o ambiente do backend possui as seguintes bibliotecas obrigatórias instaladas no ambiente virtual (`.venv`):
1. **`pypdf`** (versão `>=3.17.0`): Utilizado para decodificar, percorrer as páginas e extrair os caracteres textuais legíveis de arquivos PDF.
2. **`python-docx`** (versão `>=1.1.0`): Utilizado para ler a estrutura de documentos do Microsoft Word (`.docx`), permitindo iterar sobre os parágrafos e extrair o texto de forma limpa.

### B. Inicialização do Servidor (Resolução de Ambiente)
**IMPORTANTE:** O servidor FastAPI deve obrigatoriamente ser executado a partir do ambiente virtual do diretório `backend/` onde as dependências estão fisicamente instaladas.
* **Instalação das dependências:** `uv pip install -r requirements.txt` (a partir da pasta `backend/`).
* **Comando correto de inicialização:** Para evitar erros de importação (como `ModuleNotFoundError`), o Uvicorn deve ser executado chamando diretamente o interpretador da `.venv`:
  ```powershell
  # A partir do diretório root ou backend/
  .venv\Scripts\python.exe -m uvicorn main:app --reload
  ```
  Isso garante que todas as bibliotecas de processamento (`pypdf`, `python-docx`) sejam carregadas e resolvidas sem falhas de runtime.
