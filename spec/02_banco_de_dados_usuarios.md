# Especificação Técnica: Banco de Dados e Usuários (Integração SQLAlchemy)

Este documento especifica em alto nível técnico o design do Banco de Dados, a modelagem de entidades utilizando o **SQLAlchemy ORM** de forma nativa com **FastAPI**, o ciclo de vida das conexões, o fluxo de permissões e as políticas de segurança.

---

## 1. Escolha do Banco de Dados e ORM (SQLAlchemy Nativo)

* **Banco de Dados:** Suporte total a **MySQL** e **PostgreSQL** como motores de persistência relacional.
  * Driver MySQL: `pymysql` (conexão via `mysql+pymysql://`)
  * Driver PostgreSQL: `psycopg2` ou `psycopg2-binary` (conexão via `postgresql+psycopg2://`)
* **ORM:** **SQLAlchemy v2.0** utilizando o estilo declarativo moderno (`Mapped` e `mapped_column`) para mapeamento de tabelas.
* **Ciclo de Conexões:** Pool de conexões gerenciadas de forma síncrona/assíncrona que abrem a cada requisição HTTP e são encerradas automaticamente logo após o término da resposta (padrão *Session-per-Request*).
* **Criação de Tabelas:** Utilização do método nativo do SQLAlchemy `Base.metadata.create_all(bind=engine)` no momento de inicialização da aplicação FastAPI para garantir a integridade estrutural.

---

## 2. Especificação do Módulo de Conexão (`backend/db/connection.py`)

A comunicação entre a API e o banco de dados será definida no arquivo `backend/db/connection.py`. O código a ser implementado detecta dinamicamente o banco configurado pela variável de ambiente `DATABASE_URL`:

```python
# backend/db/connection.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 1. Definição da URL de Conexão (Lida dinamicamente do .env)
# Exemplos:
# MySQL: "mysql+pymysql://usuario:senha@localhost:3306/nome_banco"
# Postgres: "postgresql+psycopg2://usuario:senha@localhost:5432/nome_banco"
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:root@localhost:3306/pos_sistema")

# 2. Criação do Engine do Banco
# Nota: 'connect_args={"check_same_thread": False}' é aplicável apenas a SQLite (caso usado para testes)
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL, 
    connect_args=connect_args,
    pool_pre_ping=True  # Evita desconexões inesperadas do MySQL/PostgreSQL
)

# 3. Fábrica de Sessões (Sessionmaker)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

E a injeção de dependência no FastAPI em `backend/db/dependency.py`:

```python
# backend/db/dependency.py
from db.connection import SessionLocal

# Garante que cada requisição tenha sua própria sessão aberta e fechada de forma segura
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 3. Especificação do Módulo de Modelos (`backend/models/`)

Todos os modelos de dados herdarão de `Base` (definida em `backend/models/base.py`) e serão definidos no diretório `backend/models/`. O mapeamento utilizará a sintaxe robusta do SQLAlchemy v2.0:

```python
# backend/models/usuario.py
from datetime import datetime
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

# --- MODELO: Usuario ---
class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    cargo: Mapped[str] = mapped_column(String(20), default="user", nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamentos
    tokens: Mapped[list["TokenAcesso"]] = relationship("TokenAcesso", back_populates="usuario", cascade="all, delete-orphan")
    historico: Mapped[list["HistoricoAgente"]] = relationship("HistoricoAgente", back_populates="usuario")


# --- MODELO: TokenAcesso ---
class TokenAcesso(Base):
    __tablename__ = "tokens_acesso"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"), nullable=False)
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    expira_em: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revogado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relacionamentos
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="tokens")


# --- MODELO: HistoricoAgente ---
class HistoricoAgente(Base):
    __tablename__ = "historico_agentes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"), nullable=True)
    habilidade: Mapped[str] = mapped_column(String(50), nullable=False)
    input_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    output_response: Mapped[str] = mapped_column(Text, nullable=False)
    tokens_utilizados: Mapped[int] = mapped_column(Integer, nullable=True)
    executado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamentos
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="historico")
```

---

## 4. Integração das Tabelas no Startup da Aplicação

```python
# backend/main.py
from fastapi import FastAPI
from db.connection import engine
from models.base import Base
import models

app = FastAPI(title="Aula - API de IA e Gestão de Usuários")

# Comando executado na inicialização para criar todas as tabelas mapeadas e semear o administrador
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    print("Banco de dados MySQL/PostgreSQL inicializado e tabelas criadas com sucesso!")
    
    # Seeding do usuário administrador padrão se não estiver presente
    from db.connection import SessionLocal
    from core.security import obter_senha_hash
    db = SessionLocal()
    try:
        admin_user = db.query(models.usuario.Usuario).filter(models.usuario.Usuario.email == "admin@admin").first()
        if not admin_user:
            admin_old = db.query(models.usuario.Usuario).filter(models.usuario.Usuario.email == "admin@admin.com").first()
            if admin_old:
                admin_old.email = "admin@admin"
                db.commit()
                print("Usuário Administrador padrão atualizado de admin@admin.com para admin@admin")
            else:
                new_admin = models.usuario.Usuario(
                    nome="Administrador",
                    email="admin@admin",
                    senha_hash=obter_senha_hash("admin"),
                    cargo="admin",
                    ativo=True
                )
                db.add(new_admin)
                db.commit()
                print("Usuário Administrador padrão ('admin@admin' / 'admin') semeado com sucesso!")
    except Exception as e:
        print(f"Erro no seeding: {e}")
    finally:
        db.close()
```

---

## 5. Fluxo de Autenticação Segura (FastAPI & React)

```text
[Usuário] ---> (Tenta Login) ---> [React Frontend SPA]
                                       │
                                 (Chamada HTTP POST para /auth/login com credenciais)
                                       ▼
                                 [FastAPI Backend]
                                       │
                          (Verifica email/senha via hash bcrypt no DB)
                                       ▼
                        [Retorna Perfil + Token de Acesso JWT]
                                       │
    [React] <--------------------------┘
      │
(Armazena JWT no localStorage/sessionStorage de forma segura)
      ▼
[Dashboard Acessível com Bearer Token nos cabeçalhos das requisições]
```

### Segurança e Hash de Senha
* As senhas nunca serão salvas em texto plano no banco de dados.
* Utilização direta da biblioteca **`bcrypt`** de forma nativa no FastAPI para geração e validação de hashes de senhas. Isso elimina os problemas de compatibilidade e obsolescência da biblioteca `passlib`.
* Comunicação segura baseada em cabeçalhos HTTP padrão (`Authorization: Bearer <JWT>`) para todas as rotas privadas da API.
