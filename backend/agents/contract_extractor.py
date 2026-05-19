import json
from agents.base import client
from fastapi import HTTPException, status

def skill_extrair_contrato(texto_contrato: str) -> dict:
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço do Groq não configurado. Por favor, adicione GROQ_API_KEY no arquivo .env."
        )

    prompt_sistema = (
        "Você é um especialista em análise contratual jurídica.\n"
        "Seu papel é analisar o texto do contrato fornecido e extrair dados no seguinte formato JSON estrito, sem markdown extra e sem blocos de código markdown (como ```json):\n"
        "{\n"
        "  \"numero_contrato\": \"Código/Número do contrato\",\n"
        "  \"contratante\": \"Nome da empresa/entidade contratante\",\n"
        "  \"contratado\": \"Nome da empresa/entidade contratada\",\n"
        "  \"data_inicio\": \"AAAA-MM-DD\",\n"
        "  \"data_fim\": \"AAAA-MM-DD\",\n"
        "  \"valor_total\": 125000.00,\n"
        "  \"moeda\": \"BRL\",\n"
        "  \"resumo\": \"Breve resumo do objeto do contrato\"\n"
        "}\n"
        "Retorne UNICAMENTE o bloco JSON válido. Se não conseguir encontrar alguma informação, forneça um valor padrão aproximado coerente."
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": f"Texto do Contrato:\n\n{texto_contrato}"}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        resultado_str = completion.choices[0].message.content
        return json.loads(resultado_str)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha de processamento inteligente no agente: {str(e)}"
        )
