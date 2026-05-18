import os
import sys
# Adiciona a pasta raiz (django_fastapi) ao sys.path para importar o agent_skills
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Depends, Header
from sqlalchemy.orm import Session
from db.connection import engine
from db.dependency import get_db
import models
import routers
from core.security import common_api_token
from schemas.agent import Historia
from agent_skills.storyteller import skill_gerar_historia
from schemas.agent import HistoriaInput

app = FastAPI(
    title="Aula - API de IA e Gestão de Usuários",
    description="Backend FastAPI para gerenciar Habilidades de Agente e Autenticação de Usuários"
)

# Startup event to ensure physical SQLite database, tables are created and default admin is seeded
@app.on_event("startup")
def startup_event():
    models.Base.metadata.create_all(bind=engine)
    print("Banco de dados SQLite inicializado e tabelas criadas com sucesso!")
    
    # Seeding default admin credentials if not present
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
            print("Usuário Administrador padrão ('admin@admin.com' / 'admin') criado com sucesso!")
    except Exception as e:
        print(f"Erro ao criar usuário administrador padrão: {e}")
    finally:
        db.close()

# Health and status endpoints
@app.get("/", tags=["Status"])
def read_root():
    return {"message": "Servidor FastAPI rodando com sucesso!"}

@app.get("/status", tags=["Status"])
def read_status():
    return {"status": "online"}

# Legacy story generation endpoint
@app.post("/gerar_historia", tags=["Legacy Agent Skills"])
def gerar_historia(
    payload: Historia, 
    api_token: str = Depends(common_api_token),
    db: Session = Depends(get_db)
):
    # Convert legacy payload (Tema) to storyteller skill model (tema)
    skill_input = HistoriaInput(tema=payload.Tema)
    output = skill_gerar_historia(skill_input)
    
    # Log to physical database
    historico_log = models.HistoricoAgente(
        usuario_id=None,
        habilidade="legacy_storyteller",
        input_prompt=f"Tema: {payload.Tema}",
        output_response=output.historia,
        tokens_utilizados=None
    )
    db.add(historico_log)
    db.commit()
    
    return {"historia": output.historia}

# Register modular APIRouters
app.include_router(routers.auth)
app.include_router(routers.usuario)
app.include_router(routers.skills)
app.include_router(routers.math)
app.include_router(routers.contracts)
# Triggering reload after installing dependencies globally and updating model to llama-3.1-8b-instant.
