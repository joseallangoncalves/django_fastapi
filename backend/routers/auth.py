from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from core.config import settings
from core.security import verificar_senha, criar_token_acesso, common_api_token
from db.dependency import get_db
import models
from schemas.token import TokenResponse
from schemas.usuario import UsuarioResponse

router = APIRouter(prefix="/auth", tags=["Autenticação"])

class LoginRequest(BaseModel):
    email: str
    senha: str

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.email == payload.email).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos"
        )
    
    if not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Conta de usuário inativa"
        )
        
    if not verificar_senha(payload.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos"
        )
    
    # Generate JWT token
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token_str = criar_token_acesso(data={"sub": str(usuario.id)}, expires_delta=expires_delta)
    expira_em = datetime.utcnow() + expires_delta
    
    # Save token in table tokens_acesso
    db_token = models.TokenAcesso(
        usuario_id=usuario.id,
        token=token_str,
        expira_em=expira_em,
        revogado=False
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    
    return TokenResponse(
        access_token=token_str,
        token_type="bearer",
        expira_em=expira_em,
        usuario=UsuarioResponse.from_orm(usuario)
    )

@router.post("/logout")
def logout(
    authorization: str = Header(..., description="JWT Bearer Token"),
    db: Session = Depends(get_db)
):
    token_str = authorization.replace("Bearer ", "").replace("bearer ", "")
    db_token = db.query(models.TokenAcesso).filter(models.TokenAcesso.token == token_str).first()
    if db_token:
        db_token.revogado = True
        db.commit()
    return {"message": "Logout realizado com sucesso e token revogado"}
