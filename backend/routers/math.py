from fastapi import APIRouter, Depends, HTTPException, Query, status
from core.security import common_api_token
from core.config import settings
from schemas.math import Numeros, Resultado, TipoOperacao

router = APIRouter(
    prefix="/math",
    tags=["Operações matemáticas"],
    dependencies=[Depends(common_api_token)]  # Applying security token validation
)

@router.get("/soma/v1/{numero1}/{numero2}")
def soma_v1(numero1: int, numero2: int):
    resultado = numero1 + numero2
    if resultado < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resultado negativo"
        )
    return {"resultado": resultado}

# Deprecated soma_v2
@router.post("/soma/v2", deprecated=True)
def soma_v2(
    numero1: int = Query(..., description="Primeiro número"),
    numero2: int = Query(..., description="Segundo número"),
    api_token: str = Query(..., description="Legacy API token")
):
    # This route has custom parameter/token checking
    if api_token != settings.API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de API inválido"
        )
    return {"resultado": numero1 + numero2}

@router.post("/soma/v3", response_model=Resultado)
def soma_v3(payload: Numeros):
    if payload.numero1 < 0 or payload.numero2 < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Números devem ser positivos"
        )
    return Resultado(resultado=payload.numero1 + payload.numero2)

@router.post("/operacao_matematica", response_model=Resultado)
def operacao_matematica(payload: Numeros, operacao: TipoOperacao = Query(..., description="Tipo de operação matemática")):
    if operacao == TipoOperacao.soma:
        res = payload.numero1 + payload.numero2
    elif operacao == TipoOperacao.subtracao:
        res = payload.numero1 - payload.numero2
    elif operacao == TipoOperacao.multiplicacao:
        res = payload.numero1 * payload.numero2
    elif operacao == TipoOperacao.divisao:
        if payload.numero2 == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Divisão por zero não permitida"
            )
        res = payload.numero1 / payload.numero2
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Operação inválida"
        )
    return Resultado(resultado=res)
