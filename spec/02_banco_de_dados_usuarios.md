# Especificação Técnica: Banco de Dados e Usuários (Integração SQLAlchemy)

Este documento especifica em alto nível técnico o design do Banco de Dados, a modelagem de entidades utilizando o **SQLAlchemy ORM** de forma nativa com **FastAPI**, o ciclo de vida das conexões, o fluxo de permissões e as políticas de segurança.

---

## 1. Escolha do Banco de Dados e ORM (SQLAlchemy Nativo)

* **Banco de Dados:** Utilização do **SQLite** como motor local para persistência rápida em arquivo único (`pos_sistema.db`).
* **ORM:** **SQLAlchemy v2.0** utilizando o estilo declarativo moderno (`Mapped` e `mapped_column`) para mapeamento de tabelas.
* **Ciclo de Conexões:** Sessões locais gerenciadas de forma síncrona/assíncrona que abrem a cada requisição HTTP e são encerradas automaticamente logo após o término da resposta (padrão *Session-per-Request*).
* **Criação de Tabelas:** Utilização do método nativo do SQLAlchemy `Base.metadata.create_all(bind=engine)` no momento de inicialização da aplicação FastAPI para garantir a integridade estrutural sem a necessidade inicial de ferramentas externas de migração.

---

## 2. Especificação do Módulo de Conexão (`database.py`)

A comunicação entre a API e o banco de dados será definida no arquivo `pos_fast_api/database.py`. O código a ser implementado seguirá estritamente as regras de gerenciamento de dependências do FastAPI:

```python
# pos_fast_api/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Definição da URL de Conexão (SQLite local)
SQLALCHEMY_DATABASE_URL = "sqlite:///./pos_sistema.db"

# 2. Criação do Engine do Banco
# Nota: 'connect_args={"check_same_thread": False}' é necessário apenas para o SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. Fábrica de Sessões (Sessionmaker)
# autoflush=False e autocommit=False garantem controle total sobre as transações
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Classe Base Declarativa para Herança dos Modelos
Base = declarative_base()

# 5. Dependência do FastAPI (get_db)
# Garante que cada requisição tenha sua própria sessão aberta e fechada de forma segura
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 3. Especificação do Módulo de Modelos (`models.py`)

Todos os modelos de dados herdarão de `Base` (importada de `database.py`) e serão definidos em `pos_fast_api/models.py`. O mapeamento utilizará a sintaxe robusta do SQLAlchemy v2.0:

```python
# pos_fast_api/models.py
from datetime import datetime
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

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

Para garantir que o banco de dados e suas tabelas sejam criados sem scripts manuais, adicionamos a seguinte especificação ao fluxo de inicialização da aplicação. Além disso, o sistema realiza a **semeadura automática (seeding)** de um usuário administrador padrão (`admin@admin.com` / `admin`) na primeira execução:

```python
# backend/main.py
from fastapi import FastAPI
from db.connection import engine
import models

app = FastAPI(title="Aula - API de IA e Gestão de Usuários")

# Comando executado na inicialização para criar todas as tabelas mapeadas e semear o administrador
@app.on_event("startup")
def startup_event():
    models.Base.metadata.create_all(bind=engine)
    print("Banco de dados SQLite inicializado e tabelas criadas com sucesso!")
    
    # Seeding do usuário administrador padrão se não estiver presente
    from db.connection import SessionLocal
    from core.security import obter_senha_hash
    db = SessionLocal()
    try:
        admin_user = db.query(models.Usuario).filter(models.Usuario.email == "admin@admin.com").first()
        if not admin_user:
            new_admin = models.Usuario(
                nome="Administrador",
                email="admin@admin.com",
                senha_hash=obter_senha_hash("admin"),
                cargo="admin",
                ativo=True
            )
            db.add(new_admin)
            db.commit()
            print("Usuário Administrador padrão ('admin@admin.com' / 'admin') semeado com sucesso!")
    except Exception as e:
        print(f"Erro no seeding: {e}")
    finally:
        db.close()
```

---

## 5. Fluxo de Autenticação Segura (FastAPI & Django)

```text
[Usuário] ---> (Tenta Login) ---> [Django Front]
                                      │
                                 (Faz chamada POST de validação com API_TOKEN interno)
                                      ▼
                                [FastAPI Back]
                                      │
                         (Verifica email/senha via hash)
                                      ▼
                        [Retorna Perfil + Token de Sessão]
                                      │
    [Django] <------------------------┘
      │
(Cria Sessão Segura baseada em Cookie no Navegador do Usuário)
      ▼
[Dashboard Acessível]
```

### Segurança e Hash de Senha
* As senhas nunca serão salvas em texto plano no banco de dados.
* Utilização direta da biblioteca **`bcrypt`** de forma nativa no FastAPI para geração e validação de hashes de senhas. Isso elimina os problemas de compatibilidade e obsolescência da biblioteca `passlib` em ambientes modernos do Python 3.10+.
* Comunicação interna entre Django e FastAPI autenticada com uma chave de segurança robusta no cabeçalho das requisições (`X-API-Token`), definida por variáveis de ambiente.
