from pydantic import BaseModel, Field

# Legacy story schema
class Historia(BaseModel):
    Tema: str = Field(..., description="Tema da história")

# Modern story schemas
class HistoriaInput(BaseModel):
    tema: str = Field(..., description="Tema da história a ser gerada")

class HistoriaOutput(BaseModel):
    tema: str
    historia: str

# Technical Lecture schemas
class AulaInput(BaseModel):
    transcricao: str = Field(..., description="Transcrição bruta da aula")

class SecaoTEC(BaseModel):
    teoria: str = Field(..., description="Fundamentação teórica explicativa")
    exemplo: str = Field(..., description="Analogia prática e cenário real")
    codigo: str = Field(..., description="Código prático, limpo e comentado")

class AulaOutput(BaseModel):
    titulo: str
    secoes: list[SecaoTEC]
