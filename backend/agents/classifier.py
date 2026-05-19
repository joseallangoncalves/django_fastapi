import os
import re
import json
from agents.base import client
from fastapi import HTTPException, status

SKILLS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".agents", "skills")

def listar_skills_disponiveis() -> list:
    """
    Scans `.agents/skills/` directory and extracts the metadata (name, description) 
    from the YAML frontmatter of each SKILL.md.
    """
    skills = []
    if not os.path.exists(SKILLS_DIR):
        return skills
        
    for item in os.listdir(SKILLS_DIR):
        item_path = os.path.join(SKILLS_DIR, item)
        if os.path.isdir(item_path):
            skill_md_path = os.path.join(item_path, "SKILL.md")
            if os.path.exists(skill_md_path):
                try:
                    with open(skill_md_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # Regex to parse the frontmatter
                    fm_match = re.search(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
                    name = item
                    description = ""
                    instructions = content
                    
                    if fm_match:
                        fm_text = fm_match.group(1)
                        # Extract name: ...
                        name_match = re.search(r"^name:\s*(.*?)$", fm_text, re.MULTILINE)
                        if name_match:
                            name = name_match.group(1).strip()
                        # Extract description: ...
                        desc_match = re.search(r"^description:\s*(.*?)$", fm_text, re.MULTILINE)
                        if desc_match:
                            description = desc_match.group(1).strip()
                            
                        # Extract instructions (everything after the frontmatter)
                        instructions = content[fm_match.end():].strip()
                        
                    skills.append({
                        "id": item,
                        "name": name,
                        "description": description,
                        "instructions": instructions
                    })
                except Exception as e:
                    print(f"Erro ao ler a skill {item}: {e}")
    return skills

def classificar_e_rotear_documento(texto_documento: str) -> dict:
    """
    Calls the Groq LLM to classify the document content against the 15 available skills
    and returns routing recommendations.
    """
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço do Groq não configurado. Por favor, adicione GROQ_API_KEY no arquivo .env."
        )
        
    skills = listar_skills_disponiveis()
    skills_context = "\n".join([
        f"- ID da Habilidade: '{s['id']}'\n  Nome: {s['name']}\n  Descrição: {s['description']}"
        for s in skills
    ])
    
    # Send only the first 2500 characters to avoid rate limits / token bloating
    amostra_documento = texto_documento[:2500]
    
    prompt_sistema = (
        "Você é o Classificador Inteligente do Sistema de Agentes.\n"
        "Sua tarefa é analisar o texto do documento fornecido e decidir qual das habilidades listadas abaixo é a melhor correspondência.\n\n"
        "Habilidades Disponíveis:\n"
        f"{skills_context}\n\n"
        "Você deve retornar a resposta estritamente no seguinte formato JSON, sem blocos de código markdown:\n"
        "{\n"
        "  \"skill_recomendada\": \"ID da habilidade correspondente (ex: analisador-contratual ou resumo)\",\n"
        "  \"justificativa\": \"Breve explicação em português de por que essa habilidade é a melhor correspondência\",\n"
        "  \"e_contrato\": true ou false (true se o documento for um contrato legal ou minuta de contrato, false caso contrário),\n"
        "  \"plano_de_acao\": \"O que deve ser feito a seguir com o documento\"\n"
        "}\n"
        "Seja extremamente preciso."
    )
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": f"Texto do Documento:\n\n{amostra_documento}"}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        resultado_str = completion.choices[0].message.content
        return json.loads(resultado_str)
    except Exception as e:
        # Fallback in case of failure
        return {
            "skill_recomendada": "resumo",
            "justificativa": f"Falha na classificação automática ({str(e)}). Roteado para a skill de resumo por padrão.",
            "e_contrato": False,
            "plano_de_acao": "Processar documento genérico usando o resumo."
        }

def executar_skill_customizada(skill_id: str, texto_documento: str) -> str:
    """
    Executes a specific skill using the instructions loaded dynamically from its SKILL.md.
    """
    if not client:
        return "Erro: Groq client não configurado."
        
    skills = listar_skills_disponiveis()
    matched_skill = next((s for s in skills if s["id"] == skill_id), None)
    
    if not matched_skill:
        return f"Erro: Skill {skill_id} não encontrada."
        
    system_prompt = matched_skill["instructions"]
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Conteúdo do Documento:\n\n{texto_documento[:5000]}"}
            ],
            temperature=0.3
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Falha ao executar a skill {skill_id}: {str(e)}"
