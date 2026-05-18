from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

# Common base class
class UsuarioBase(BaseModel):
    nome: str = Field(..., max_length=100, description="Nome completo do usuário")
    email: EmailStr = Field(..., description="Endereço de email válido e único")
    cargo: str = Field("user", max_length=20, description="Nível de acesso (admin, user)")

# Schema for user creation
class UsuarioCreate(UsuarioBase):
    senha: str = Field(..., min_length=6, description="Senha com no mínimo 6 caracteres")

# Schema for user update
class UsuarioUpdate(BaseModel):
    nome: str | None = Field(None, max_length=100)
    email: EmailStr | None = None
    cargo: str | None = Field(None, max_length=20)
    ativo: bool | None = None
    senha: str | None = Field(None, min_length=6, description="Nova senha se for atualizar")

# Schema returned by API (hides password hashes)
class UsuarioResponse(UsuarioBase):
    id: int
    ativo: bool
    criado_em: datetime

    class Config:
        from_attributes = True  # Allows direct compatibility with SQLAlchemy models
