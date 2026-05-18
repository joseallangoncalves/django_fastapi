from datetime import datetime, timedelta
from typing import Optional
from fastapi import Header, HTTPException, Query, status, Depends
from passlib.context import CryptContext
import jwt
from core.config import settings

import bcrypt

def obter_senha_hash(senha: str) -> str:
    pwd_bytes = senha.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verificar_senha(senha_pura: str, senha_hash: str) -> bool:
    try:
        return bcrypt.checkpw(senha_pura.encode('utf-8'), senha_hash.encode('utf-8'))
    except Exception:
        return False

def criar_token_acesso(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verificar_token_acesso(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

# Dependency to check fixed API token (for server-to-server or legacy math/story validation)
def common_api_token(
    api_token: Optional[str] = Query(None, description="Legacy API token passed via query string"),
    x_api_token: Optional[str] = Header(None, alias="X-API-Token", description="API token passed via header")
):
    # Log received tokens as specified in the docs
    received_token = api_token or x_api_token
    print(f"Token de API recebido: {received_token}")
    
    if received_token != settings.API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de API inválido"
        )
    return received_token
