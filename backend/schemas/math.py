from enum import Enum
from pydantic import BaseModel, Field

class TipoOperacao(str, Enum):
    soma = "soma"
    subtracao = "subtracao"
    multiplicacao = "multiplicacao"
    divisao = "divisao"

class Numeros(BaseModel):
    numero1: int = Field(..., description="Primeiro número")
    numero2: int = Field(..., description="Segundo número")

class Resultado(BaseModel):
    resultado: float = Field(..., description="Resultado da operação matemática")
