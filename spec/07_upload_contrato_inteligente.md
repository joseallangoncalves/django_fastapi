# Especificação Técnica: Upload de Contrato e Extração de Dados Inteligentes (IA)

Este documento especifica a arquitetura, o fluxo de dados, os schemas e os endpoints para a nova funcionalidade de **Upload e Processamento Inteligente de Contratos** integrada ao ecossistema Django/FastAPI com suporte a IA autônoma via Groq.

---

## 1. Visão Geral do Fluxo

A funcionalidade permitirá ao usuário carregar um arquivo de contrato nos formatos **PDF, DOC/DOCX, TXT ou Markdown (`.md`)** através de uma interface amigável. O sistema extrairá e processará o texto do contrato utilizando um agente de inteligência artificial da Groq para obter os metadados essenciais e persistir estes registros estruturados no banco de dados SQLite local.

```text
[Usuário] ---> (Envia arquivo de Contrato) ---> [Portal Django (Front)]
                                                   │
                                            (Envia via multipart/form-data)
                                                   ▼
                                             [FastAPI (Back)]
                                                   │
                                     (Lê e extrai texto do contrato)
                                                   ▼
                                         [Agente de IA (Groq)]
                                                   │
                                     (Extrai JSON Estruturado de Dados)
                                                   ▼
                                         [Banco de Dados SQLite]
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

## 5. Nova Habilidade de Agente (`agent_skills/contract_extractor.py`)

Esta habilidade fará o parsing inteligente do texto usando o Groq LLM com parâmetros JSON estruturados para garantir retorno estrito e correto de dados:

```python
# agent_skills/contract_extractor.py
import json
from agent_skills.base import client
from fastapi import HTTPException, status

def skill_extrair_contrato(texto_contrato: str) -> dict:
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço do Groq não configurado. Por favor, adicione GROQ_API_KEY no arquivo .env."
        )

    prompt_sistema = (
        "Você é um especialista em análise contratual jurídica. "
        "Seu papel é analisar o texto do contrato fornecido e extrair dados no seguinte formato JSON estrito, sem markdown extra:\n"
        "{\n"
        "  \"numero_contrato\": \"Código/Número do contrato\",\n"
        "  \"contratante\": \"Nome da empresa/entidade contratante\",\n"
        "  \"contratado\": \"Nome da empresa/entidade contratada\",\n"
        "  \"data_inicio\": \"AAAA-MM-DD\",\n"
        "  \"data_fim\": \"AAAA-MM-DD\",\n"
        "  \"valor_total\": 125000.00,\n"
        "  \"moeda\": \"BRL\",\n"
        "  \"resumo\": \"Breve resumo do objeto do contrato\"\n"
        "}\n"
        "Retorne UNICAMENTE o bloco JSON válido. Se não conseguir encontrar alguma informação, forneça um valor padrão aproximado coerente."
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": f"Texto do Contrato:\n\n{texto_contrato}"}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        resultado_str = completion.choices[0].message.content
        return json.loads(resultado_str)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha de processamento inteligente no agente: {str(e)}"
        )
```

---

## 6. Endpoints do Backend (FastAPI)

Adicionaremos um novo router `backend/routers/contracts.py` protegendo os seguintes endpoints:

* **`POST /contracts/upload`**: Recebe o arquivo de contrato via `UploadFile` contendo suporte aos seguintes formatos de arquivo:
  * **`.txt` / `.md`**: Lidos decodificando o arquivo binário em texto. Se o texto exceder 12.000 caracteres, ele é truncado mantendo o início e o fim.
  * **`.pdf`**: Processado utilizando a biblioteca `pypdf`. Se o PDF possuir mais de 4 páginas, lê-se apenas as 3 primeiras páginas e a última página. Se o texto concatenado exceder 12.000 caracteres, ele é truncado (primeiros 9.000 e últimos 3.000 caracteres) para respeitar os limites de TPM (Tokens Per Minute) da API da Groq Cloud.
  * **`.docx` / `.doc`**: Lidos utilizando a biblioteca `python-docx`. Se o texto exceder 12.000 caracteres, ele é truncado da mesma forma.
  * *Após extrair e tratar/truncar de forma inteligente o texto bruto, o endpoint aciona a habilidade `skill_extrair_contrato` usando o modelo `llama-3.1-8b-instant` (otimizado para alta velocidade e suporte a JSON nativo), persiste a entidade no banco de dados SQLite associada ao usuário autenticado e registra a execução no histórico.*
* **`GET /contracts/`**: Lista todos os contratos analisados e persistidos do usuário autenticado.
* **`GET /contracts/{contract_id}`**: Visualiza em detalhe um contrato específico pelo ID, garantindo que o contrato pertença ao usuário autenticado.
* **`PUT /contracts/{contract_id}`**: Permite a edição/atualização manual das informações do contrato (ex: ajustar um valor ou data extraída incorretamente).
* **`DELETE /contracts/{contract_id}`**: Exclui fisicamente do banco de dados o contrato especificado, liberando espaço e atualizando as estatísticas do painel. Esta rota é ativada via front-end pelos botões "Excluir Registro" nas interfaces de detalhes e lista de contratos, efetuando a exclusão em cascata.

---

## 7. Integração com Frontend (Django)

* **Interface Visual**: Criaremos uma página com formulário de upload de arquivos com área *Drag and Drop* (arrastar e soltar), aceitando explicitamente as extensões `.pdf`, `.doc`, `.docx`, `.txt` e `.md` (estilizado em CSS moderno e animado).
* **Painel de Resultados**: Uma exibição em estilo de cartões interativos mostrando os detalhes extraídos (Número, Contratante, Contratado, Datas, Valor e o Resumo da IA).
* **Persistência**: Uma chamada síncrona `httpx.post` multipart do Django BFF para o FastAPI transmitindo o arquivo carregado de forma transparente.

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
