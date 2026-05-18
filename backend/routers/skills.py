from datetime import datetime
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from core.security import verificar_token_acesso, common_api_token
from db.dependency import get_db
import models
from schemas.agent import HistoriaInput, HistoriaOutput, AulaInput, AulaOutput
from agent_skills.storyteller import skill_gerar_historia
from agent_skills.lecture_extractor import skill_extrair_aula

router = APIRouter(
    prefix="/skills", 
    tags=["Agent Skills"],
    dependencies=[Depends(common_api_token)]  # Secure all skill routes using the system token
)

def _get_authenticated_user_id(authorization: str | None) -> int | None:
    if not authorization:
        return None
    try:
        token_str = authorization.replace("Bearer ", "").replace("bearer ", "")
        payload = verificar_token_acesso(token_str)
        if payload and "sub" in payload:
            return int(payload["sub"])
    except Exception:
        pass
    return None

@router.post("/storyteller", response_model=HistoriaOutput)
def execute_storyteller(
    payload: HistoriaInput,
    authorization: str | None = Header(None, description="Opcional: JWT Bearer Token do usuário logado"),
    db: Session = Depends(get_db)
):
    # Retrieve authenticated user ID if logged in
    user_id = _get_authenticated_user_id(authorization)
    
    # Run the skill logic
    output = skill_gerar_historia(payload)
    
    # Log execution in historico_agentes table
    historico_log = models.HistoricoAgente(
        usuario_id=user_id,
        habilidade="storyteller",
        input_prompt=f"Tema: {payload.tema}",
        output_response=output.historia,
        tokens_utilizados=None,  # Or parse from Groq meta if available
        executado_em=datetime.utcnow()
    )
    db.add(historico_log)
    db.commit()
    
    return output

@router.post("/lecture_extractor", response_model=AulaOutput)
def execute_lecture_extractor(
    payload: AulaInput,
    authorization: str | None = Header(None, description="Opcional: JWT Bearer Token do usuário logado"),
    db: Session = Depends(get_db)
):
    # Retrieve authenticated user ID if logged in
    user_id = _get_authenticated_user_id(authorization)
    
    # Run the skill logic
    output = skill_extrair_aula(payload)
    
    # Format a text response for the DB log
    secoes_str = []
    for idx, sec in enumerate(output.secoes):
        secoes_str.append(f"Seção {idx + 1}:\n- Teoria: {sec.teoria[:100]}...\n- Exemplo: {sec.exemplo[:100]}...\n- Código: {sec.codigo[:100]}...")
    output_text = f"Título: {output.titulo}\n" + "\n".join(secoes_str)
    
    # Log execution in historico_agentes table
    historico_log = models.HistoricoAgente(
        usuario_id=user_id,
        habilidade="tec_lecture",
        input_prompt=payload.transcricao[:1000] + "..." if len(payload.transcricao) > 1000 else payload.transcricao,
        output_response=output_text,
        tokens_utilizados=None,
        executado_em=datetime.utcnow()
    )
    db.add(historico_log)
    db.commit()
    
    return output

@router.get("/history")
def get_history(
    authorization: str | None = Header(None, description="JWT Bearer Token"),
    db: Session = Depends(get_db)
):
    user_id = _get_authenticated_user_id(authorization)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autorizado"
        )
    logs = db.query(models.HistoricoAgente).filter(models.HistoricoAgente.usuario_id == user_id).order_by(models.HistoricoAgente.executado_em.desc()).all()
    return [
        {
            "id": log.id,
            "habilidade": log.habilidade,
            "input_prompt": log.input_prompt,
            "output_response": log.output_response,
            "executado_em": log.executado_em.isoformat()
        }
        for log in logs
    ]

