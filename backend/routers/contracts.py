import io
import os
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from db.dependency import get_db
from core.security import verificar_token_acesso, common_api_token
import models
from schemas.contrato import ContratoCreate, ContratoUpdate, ContratoOutput
from agents.contract_extractor import skill_extrair_contrato

router = APIRouter(
    prefix="/contracts",
    tags=["Gestão de Contratos Inteligentes"],
    dependencies=[Depends(common_api_token)]
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

async def _extract_text_from_file(file: UploadFile) -> str:
    filename = file.filename.lower()
    content = await file.read()
    
    if filename.endswith((".txt", ".md")):
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                text = content.decode("latin-1")
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Não foi possível decodificar o arquivo de texto: {str(e)}"
                )
        if len(text) > 12000:
            text = text[:9000] + "\n... [Texto intermediário omitido para evitar limite de tokens] ...\n" + text[-3000:]
        return text
                
    elif filename.endswith(".pdf"):
        try:
            import pypdf
            pdf_reader = pypdf.PdfReader(io.BytesIO(content))
            text_parts = []
            num_pages = len(pdf_reader.pages)
            
            # Se o PDF for muito grande, pegamos as 3 primeiras páginas e a última página
            if num_pages > 4:
                for i in range(3):
                    text = pdf_reader.pages[i].extract_text()
                    if text:
                        text_parts.append(text)
                # Adiciona a última página que costuma ter assinaturas e valores/datas finais
                last_text = pdf_reader.pages[num_pages - 1].extract_text()
                if last_text:
                    text_parts.append(f"\n--- ÚLTIMA PÁGINA ---\n{last_text}")
            else:
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
                        
            extracted_text = "\n".join(text_parts).strip()
            
            # Trunca o texto se ele ainda for excessivamente longo para evitar rate limit
            # 12.000 caracteres é cerca de ~3.000 tokens, o que fica bem abaixo do limite de 6.000 TPM
            if len(extracted_text) > 12000:
                extracted_text = extracted_text[:9000] + "\n... [Texto intermediário omitido para evitar limite de tokens] ...\n" + extracted_text[-3000:]
                
            if not extracted_text:
                raise ValueError("Nenhum caractere textual legível pôde ser extraído do PDF.")
            return extracted_text
        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="A biblioteca 'pypdf' necessária para leitura de PDFs não está instalada no servidor."
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro ao processar o arquivo PDF: {str(e)}"
            )
            
    elif filename.endswith(".docx"):
        try:
            import docx
            doc = docx.Document(io.BytesIO(content))
            text_parts = [p.text for p in doc.paragraphs]
            extracted_text = "\n".join(text_parts).strip()
            
            # Trunca o texto se ele for excessivamente longo para evitar rate limit
            if len(extracted_text) > 12000:
                extracted_text = extracted_text[:9000] + "\n... [Texto intermediário omitido para evitar limite de tokens] ...\n" + extracted_text[-3000:]
                
            if not extracted_text:
                raise ValueError("Nenhum caractere textual legível pôde ser extraído do DOCX.")
            return extracted_text
        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="A biblioteca 'python-docx' necessária para leitura de arquivos Word (.docx) não está instalada no servidor."
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro ao processar o arquivo Word: {str(e)}"
            )
            
    elif filename.endswith(".doc"):
        # Legacy .doc file type warning or simple text fallback
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivos de extensão '.doc' (legados) não são diretamente legíveis de forma síncrona. Por favor, salve o arquivo como '.docx' ou envie em formato '.pdf' / '.txt'."
        )
        
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de arquivo não suportado. Por favor, envie arquivos do tipo PDF, DOCX, TXT ou MD."
        )

@router.post("/upload", response_model=ContratoOutput, status_code=status.HTTP_201_CREATED)
async def upload_contrato(
    file: UploadFile = File(...),
    authorization: str | None = Header(None, description="Opcional: JWT Bearer Token do usuário logado"),
    db: Session = Depends(get_db)
):
    user_id = _get_authenticated_user_id(authorization)
    
    # 1. Extração do texto bruta conforme formato
    texto_bruto = await _extract_text_from_file(file)
    
    # 2. Classificação Automática e Roteamento via Agente Classifier
    from agents.classifier import classificar_e_rotear_documento, executar_skill_customizada
    
    recomendacao = classificar_e_rotear_documento(texto_bruto)
    skill_recomendada = recomendacao.get("skill_recomendada", "resumo")
    justificativa = recomendacao.get("justificativa", "Processamento automático de documentos.")
    e_contrato = recomendacao.get("e_contrato", False) or (skill_recomendada == "analisador-contratual")
    
    if e_contrato:
        # Se for contrato, processa com a habilidade de extração estruturada de contratos
        dados_extraidos = skill_extrair_contrato(texto_bruto)
        resumo_conteudo = dados_extraidos.get("resumo", "")
        observacao_meta = f"[Agente Smart Router: {skill_recomendada}] {justificativa}"
    else:
        # Caso contrário, executa dinamicamente a skill correspondente do .agents/skills/
        resultado_skill = executar_skill_customizada(skill_recomendada, texto_bruto)
        
        # Mapeia para a estrutura da entidade do banco de dados de forma genérica
        dados_extraidos = {
            "numero_contrato": f"DOC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "contratante": f"Skill: {skill_recomendada}",
            "contratado": "Processamento Dinâmico",
            "valor_total": 0.0,
            "moeda": "BRL",
            "resumo": resultado_skill[:1000] # O resumo armazena o output da skill correspondente
        }
        resumo_conteudo = resultado_skill
        observacao_meta = f"[Agente Smart Router: {skill_recomendada}] Justificativa: {justificativa}"
    
    # 3. Tratamento de datas
    try:
        data_ini = datetime.strptime(dados_extraidos.get("data_inicio"), "%Y-%m-%d")
        data_fim = datetime.strptime(dados_extraidos.get("data_fim"), "%Y-%m-%d")
    except Exception:
        # Fallbacks em caso de formato incorreto da IA ou documento genérico
        data_ini = datetime.combine(datetime.now().date(), datetime.min.time())
        data_fim = datetime.combine(datetime.now().date(), datetime.min.time())
        
    # 4. Criação da entidade e persistência física no banco SQLite
    novo_contrato = models.Contrato(
        usuario_id=user_id,
        numero_contrato=dados_extraidos.get("numero_contrato", f"CTR-{datetime.now().strftime('%Y%m%d%H%M%S')}"),
        contratante=dados_extraidos.get("contratante", "Desconhecido"),
        contratado=dados_extraidos.get("contratado", "Desconhecido"),
        data_inicio=data_ini,
        data_fim=data_fim,
        valor_total=float(dados_extraidos.get("valor_total", 0.0)),
        moeda=dados_extraidos.get("moeda", "BRL"),
        resumo=resumo_conteudo,
        observacoes=observacao_meta
    )
    
    try:
        db.add(novo_contrato)
        db.commit()
        db.refresh(novo_contrato)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao persistir o documento no banco de dados (provável número/ID duplicado): {str(e)}"
        )
        
    # 5. Log de execução do Agente de IA na tabela de histórico
    historico_log = models.HistoricoAgente(
        usuario_id=user_id,
        habilidade=f"smart_router_{skill_recomendada}",
        input_prompt=f"Nome do arquivo: {file.filename}\nTamanho: {len(texto_bruto)} caracteres.",
        output_response=f"Justificativa: {justificativa}\nExecutado com sucesso.",
        executado_em=datetime.utcnow()
    )
    db.add(historico_log)
    db.commit()
    
    return novo_contrato

@router.get("/", response_model=List[ContratoOutput])
def listar_contratos(
    authorization: str | None = Header(None, description="JWT Bearer Token"),
    db: Session = Depends(get_db)
):
    user_id = _get_authenticated_user_id(authorization)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autorizado"
        )
    return db.query(models.Contrato).filter(models.Contrato.usuario_id == user_id).order_by(models.Contrato.criado_em.desc()).all()

@router.get("/{contract_id}", response_model=ContratoOutput)
def obter_contrato(
    contract_id: int,
    authorization: str | None = Header(None, description="JWT Bearer Token"),
    db: Session = Depends(get_db)
):
    user_id = _get_authenticated_user_id(authorization)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autorizado"
        )
    contrato = db.query(models.Contrato).filter(models.Contrato.id == contract_id, models.Contrato.usuario_id == user_id).first()
    if not contrato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contrato não encontrado"
        )
    return contrato

@router.put("/{contract_id}", response_model=ContratoOutput)
def atualizar_contrato(
    contract_id: int,
    payload: ContratoUpdate,
    authorization: str | None = Header(None, description="JWT Bearer Token"),
    db: Session = Depends(get_db)
):
    user_id = _get_authenticated_user_id(authorization)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autorizado"
        )
    contrato = db.query(models.Contrato).filter(models.Contrato.id == contract_id, models.Contrato.usuario_id == user_id).first()
    if not contrato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contrato não encontrado"
        )
        
    # Atualizações dos campos opcionais
    if payload.numero_contrato is not None:
        contrato.numero_contrato = payload.numero_contrato
    if payload.contratante is not None:
        contrato.contratante = payload.contratante
    if payload.contratado is not None:
        contrato.contratado = payload.contratado
    if payload.data_inicio is not None:
        contrato.data_inicio = datetime.combine(payload.data_inicio, datetime.min.time())
    if payload.data_fim is not None:
        contrato.data_fim = datetime.combine(payload.data_fim, datetime.min.time())
    if payload.valor_total is not None:
        contrato.valor_total = payload.valor_total
    if payload.moeda is not None:
        contrato.moeda = payload.moeda
    if payload.resumo is not None:
        contrato.resumo = payload.resumo
    if payload.observacoes is not None:
        contrato.observacoes = payload.observacoes
        
    try:
        db.commit()
        db.refresh(contrato)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao salvar atualizações (número de contrato possivelmente duplicado): {str(e)}"
        )
    return contrato

@router.delete("/{contract_id}")
def excluir_contrato(
    contract_id: int,
    authorization: str | None = Header(None, description="JWT Bearer Token"),
    db: Session = Depends(get_db)
):
    user_id = _get_authenticated_user_id(authorization)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autorizado"
        )
    contrato = db.query(models.Contrato).filter(models.Contrato.id == contract_id, models.Contrato.usuario_id == user_id).first()
    if not contrato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contrato não encontrado"
        )
    db.delete(contrato)
    db.commit()
    return {"message": "Contrato excluído com sucesso"}
# Triggering reload after installing dependencies globally.
