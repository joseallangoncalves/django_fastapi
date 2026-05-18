from datetime import datetime
from sqlalchemy import Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

class Contrato(Base):
    __tablename__ = "contratos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=True)
    numero_contrato: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    contratante: Mapped[str] = mapped_column(String(100), nullable=False)
    contratado: Mapped[str] = mapped_column(String(100), nullable=False)
    data_inicio: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    data_fim: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    valor_total: Mapped[float] = mapped_column(Float, nullable=False)
    moeda: Mapped[str] = mapped_column(String(10), default="BRL", nullable=False)
    resumo: Mapped[str] = mapped_column(Text, nullable=True)
    observacoes: Mapped[str] = mapped_column(Text, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamento de volta com Usuario se necessário
    usuario = relationship("Usuario", back_populates="contratos")
