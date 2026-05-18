# Especificação Técnica: Rotas Modulares e Operações CRUD (FastAPI APIRouter)

Este documento especifica a arquitetura de roteamento da API e detalha individualmente cada endpoint, método HTTP, parâmetros de entrada, corpo de requisição (schemas Pydantic), lógica de banco de dados (SQLAlchemy) e modelos de resposta esperados. 

Para assegurar a modularidade e facilidade de manutenção, os controladores de rotas serão divididos em arquivos separados dentro do diretório `pos_fast_api/routers/`.

---

## 1. Arquitetura de Registro de Roteadores (`main.py`)

O arquivo principal `main.py` atuará como um orquestrador leve. Ele será responsável apenas por instanciar a aplicação FastAPI, rodar as tabelas de banco de dados e incluir os roteadores específicos:

```python
# backend/main.py (Blueprint de Roteamento)
from fastapi import FastAPI
from db.connection import engine
import models
from routers import usuario, auth, skills, math, contracts

app = FastAPI(title="Aula - API de IA e Gestão de Usuários")

# Garante criação de tabelas na inicialização
@app.on_event("startup")
def startup_event():
    models.Base.metadata.create_all(bind=engine)

# Inclusão dos roteadores modulares com prefixes e tags organizadas
app.include_router(auth.router)
app.include_router(usuario.router)
app.include_router(skills.router)
app.include_router(math.router)
app.include_router(contracts.router)
```

---

## 2. Camada de Validação: Schemas Pydantic (`schemas/usuario.py`)

Para manter a separação de camadas descrita na especificação de arquitetura, utilizaremos schemas Pydantic no arquivo `pos_fast_api/schemas/usuario.py` para validar todas as entradas e saídas de usuários:

```python
# pos_fast_api/schemas/usuario.py
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

# Classe base com atributos comuns
class UsuarioBase(BaseModel):
    nome: str = Field(..., max_length=100, description="Nome completo do usuário")
    email: EmailStr = Field(..., description="Endereço de email válido e único")
    cargo: str = Field("user", max_length=20, description="Nível de acesso (admin, user)")

# Schema enviado para criação (Adicionar)
class UsuarioCreate(UsuarioBase):
    senha: str = Field(..., min_length=6, description="Senha com no mínimo 6 caracteres")

# Schema enviado para atualização (Update)
class UsuarioUpdate(BaseModel):
    nome: str | None = Field(None, max_length=100)
    email: EmailStr | None = None
    cargo: str | None = Field(None, max_length=20)
    ativo: bool | None = None
    senha: str | None = Field(None, min_length=6, description="Nova senha se for atualizar")

# Schema retornado pela API (Sem expor hashes de senha)
class UsuarioResponse(UsuarioBase):
    id: int
    ativo: bool
    criado_em: datetime

    class Config:
        from_attributes = True  # Permite compatibilidade direta com SQLAlchemy
```

---

## 3. Especificação do Roteador de Usuários (`routers/usuario.py`)

O arquivo `pos_fast_api/routers/usuario.py` implementará o padrão completo de **CRUD** síncrono. Todas as rotas injetam a dependência `get_db` para se comunicar de forma segura com o SQLAlchemy.

### A. Assinatura do Roteador
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.dependency import get_db
import models
from schemas import usuario as schemas_user
from core.security import obter_senha_hash # Para hashing bcrypt

router = APIRouter(prefix="/usuarios", tags=["Gestão de Usuários"])
```

### B. Especificação das Rotas

#### 1. Criar Usuário (Adicionar / POST)
* **Endpoint:** `POST /usuarios/`
* **Status de Sucesso:** `201 Created`
* **Corpo de Entrada:** `schemas_user.UsuarioCreate`
* **Saída:** `schemas_user.UsuarioResponse`
* **Regras de Negócio:**
  * Verifica se o `email` fornecido já existe no banco de dados. Caso exista, retorna uma exceção `400 Bad Request` com a mensagem `"Email já cadastrado"`.
  * Realiza o hash da senha fornecida usando `bcrypt` antes de persistir no banco.
  
```python
@router.post("/", response_model=schemas_user.UsuarioResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(payload: schemas_user.UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = db.query(models.Usuario).filter(models.Usuario.email == payload.email).first()
    if db_usuario:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email já cadastrado")
    
    novo_usuario = models.Usuario(
        nome=payload.nome,
        email=payload.email,
        senha_hash=obter_senha_hash(payload.senha),
        cargo=payload.cargo
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario
```

---

#### 2. Listar Todos os Usuários (Listar / GET)
* **Endpoint:** `GET /usuarios/`
* **Status de Sucesso:** `200 OK`
* **Saída:** `list[schemas_user.UsuarioResponse]`
* **Parâmetros de Query:** `skip` (inteiro, padrão `0`), `limit` (inteiro, padrão `100`).

```python
@router.get("/", response_model=list[schemas_user.UsuarioResponse])
def listar_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    usuarios = db.query(models.Usuario).offset(skip).limit(limit).all()
    return usuarios
```

---

#### 3. Visualizar Usuário por ID (GET)
* **Endpoint:** `GET /usuarios/{id}`
* **Status de Sucesso:** `200 OK`
* **Parâmetro de Rota:** `id` (inteiro)
* **Saída:** `schemas_user.UsuarioResponse`
* **Regras de Negócio:**
  * Busca o usuário no banco pelo ID informado. Se não encontrar, retorna uma exceção `404 Not Found` informando `"Usuário não encontrado"`.

```python
@router.get("/{id}", response_model=schemas_user.UsuarioResponse)
def obter_usuario(id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return usuario
```

---

#### 4. Atualizar Usuário por ID (Editar / PUT)
* **Endpoint:** `PUT /usuarios/{id}`
* **Status de Sucesso:** `200 OK`
* **Parâmetro de Rota:** `id` (inteiro)
* **Corpo de Entrada:** `schemas_user.UsuarioUpdate`
* **Saída:** `schemas_user.UsuarioResponse`
* **Regras de Negócio:**
  * Busca o usuário pelo ID. Se não existir, retorna `404 Not Found`.
  * Se o email for atualizado, verifica se o novo email já pertence a outro usuário para evitar duplicidade.
  * Se uma nova senha for fornecida, gera um novo hash seguro (`bcrypt`).

```python
@router.put("/{id}", response_model=schemas_user.UsuarioResponse)
def atualizar_usuario(id: int, payload: schemas_user.UsuarioUpdate, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    
    # Atualiza apenas os campos enviados no payload
    if payload.nome is not None:
        usuario.nome = payload.nome
    if payload.email is not None:
        # Verifica duplicidade de email
        email_existente = db.query(models.Usuario).filter(models.Usuario.email == payload.email, models.Usuario.id != id).first()
        if email_existente:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email já em uso por outro usuário")
        usuario.email = payload.email
    if payload.cargo is not None:
        usuario.cargo = payload.cargo
    if payload.ativo is not None:
        usuario.ativo = payload.ativo
    if payload.senha is not None:
        usuario.senha_hash = obter_senha_hash(payload.senha)
        
    db.commit()
    db.refresh(usuario)
    return usuario
```

---

#### 5. Deletar Usuário por ID (Excluir / DELETE)
* **Endpoint:** `DELETE /usuarios/{id}`
* **Status de Sucesso:** `200 OK`
* **Parâmetro de Rota:** `id` (inteiro)
* **Saída:** `{"message": "Usuário excluído com sucesso"}`
* **Regras de Negócio:**
  * Busca o usuário pelo ID. Se não encontrar, retorna `404 Not Found`.
  * Executa a remoção. Devido às restrições do banco (especificadas no dicionário de dados), os tokens associados serão apagados em cascata e seus históricos de auditoria de IA terão o `usuario_id` definido como `null`.

```python
@router.delete("/{id}")
def excluir_usuario(id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    
    db.delete(usuario)
    db.commit()
    return {"message": "Usuário excluído com sucesso"}
```
