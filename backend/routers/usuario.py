from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.dependency import get_db
import models
from schemas import usuario as schemas_user
from core.security import obter_senha_hash, common_api_token

router = APIRouter(
    prefix="/usuarios", 
    tags=["Gestão de Usuários"],
    dependencies=[Depends(common_api_token)]  # Secure all user CRUD endpoints
)

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

@router.get("/", response_model=list[schemas_user.UsuarioResponse])
def listar_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    usuarios = db.query(models.Usuario).offset(skip).limit(limit).all()
    return usuarios

@router.get("/{id}", response_model=schemas_user.UsuarioResponse)
def obter_usuario(id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return usuario

@router.put("/{id}", response_model=schemas_user.UsuarioResponse)
def atualizar_usuario(id: int, payload: schemas_user.UsuarioUpdate, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    
    # Update only fields sent in payload
    if payload.nome is not None:
        usuario.nome = payload.nome
    if payload.email is not None:
        # Check email uniqueness
        email_existente = db.query(models.Usuario).filter(
            models.Usuario.email == payload.email, 
            models.Usuario.id != id
        ).first()
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

@router.delete("/{id}")
def excluir_usuario(id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    
    db.delete(usuario)
    db.commit()
    return {"message": "Usuário excluído com sucesso"}
