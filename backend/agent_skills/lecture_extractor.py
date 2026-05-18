import json
from fastapi import HTTPException, status
from agent_skills.base import client
from schemas.agent import AulaInput, AulaOutput

def skill_extrair_aula(data: AulaInput) -> AulaOutput:
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço do Groq não configurado. Por favor, adicione GROQ_API_KEY no arquivo .env."
        )
    
    system_prompt = (
        "Você é um agente de IA especializado em processamento didático e técnico de materiais educacionais. "
        "Sua tarefa é analisar uma transcrição de aula e estruturá-la no padrão T-E-C (Teoria, Exemplo, Código). "
        "Você deve organizar o conteúdo em seções lógicas conceituais.\n\n"
        "Você DEVE retornar a resposta estritamente como um objeto JSON que obedece à seguinte estrutura:\n"
        "{\n"
        "  \"titulo\": \"Título Geral da Aula\",\n"
        "  \"secoes\": [\n"
        "    {\n"
        "      \"teoria\": \"Fundamentação teórica rigorosa do conceito\",\n"
        "      \"exemplo\": \"Analogia prática ou caso de uso no mundo real\",\n"
        "      \"codigo\": \"Código-fonte funcional completo e muito bem comentado linha a linha\"\n"
        "    }\n"
        "  ]\n"
        "}\n\n"
        "Retorne APENAS o JSON válido. Não inclua nenhuma introdução ou conclusão ou blocos de marcação de markdown (como ```json) no início ou fim."
    )

    user_prompt = f"Aqui está a transcrição bruta da aula:\n\n{data.transcricao}"
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        raw_response = chat_completion.choices[0].message.content
        parsed_json = json.loads(raw_response)
        
        # Validating using Pydantic model
        return AulaOutput(**parsed_json)
    except json.JSONDecodeError as jde:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Erro de decodificação JSON do modelo Groq: {str(jde)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Falha na API do Groq ao extrair aula: {str(e)}"
        )
