from datetime import datetime
from pydantic import BaseModel
from schemas.usuario import UsuarioResponse

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expira_em: datetime
    usuario: UsuarioResponse

    class Config:
        from_attributes = True

class TokenPayload(BaseModel):
    sub: str | None = None
    exp: int | None = None
