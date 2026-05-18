from fastapi import HTTPException, status
from agent_skills.base import client
from schemas.agent import HistoriaInput, HistoriaOutput

def skill_gerar_historia(data: HistoriaInput) -> HistoriaOutput:
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço do Groq não configurado. Por favor, adicione GROQ_API_KEY no arquivo .env."
        )
    
    prompt = f"Escreva uma história sobre o tema: {data.tema}"
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.1-8b-instant",
        )
        
        conteudo = chat_completion.choices[0].message.content
        return HistoriaOutput(tema=data.tema, historia=conteudo)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Falha na API do Groq: {str(e)}"
        )
