from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
from typing import Optional, Any

class ContratoBase(BaseModel):
    numero_contrato: str = Field(..., description="Número identificador do contrato")
    contratante: str = Field(..., description="Razão Social ou Nome do Contratante")
    contratado: str = Field(..., description="Razão Social ou Nome do Contratado")
    data_inicio: date = Field(..., description="Data de início do contrato")
    data_fim: date = Field(..., description="Data de término do contrato")
    valor_total: float = Field(..., description="Valor total em formato flutuante")
    moeda: str = Field("BRL", description="Moeda sob a qual o contrato foi regido")
    resumo: Optional[str] = Field(None, description="Resumo do objeto contratual gerado pela IA")
    observacoes: Optional[str] = Field(None, description="Observações ou anotações manuais adicionadas ao contrato")

    @field_validator("data_inicio", "data_fim", mode="before")
    @classmethod
    def convert_datetime_to_date(cls, v: Any) -> Any:
        if isinstance(v, datetime):
            return v.date()
        return v

class ContratoCreate(BaseModel):
    numero_contrato: str
    contratante: str
    contratado: str
    data_inicio: date
    data_fim: date
    valor_total: float
    moeda: str = "BRL"
    resumo: Optional[str] = None
    observacoes: Optional[str] = None

class ContratoUpdate(BaseModel):
    numero_contrato: Optional[str] = None
    contratante: Optional[str] = None
    contratado: Optional[str] = None
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    valor_total: Optional[float] = None
    moeda: Optional[str] = None
    resumo: Optional[str] = None
    observacoes: Optional[str] = None

class ContratoOutput(ContratoBase):
    id: int
    criado_em: datetime

    class Config:
        from_attributes = True
