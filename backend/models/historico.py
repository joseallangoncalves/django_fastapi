from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

class HistoricoAgente(Base):
    __tablename__ = "historico_agentes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    habilidade: Mapped[str] = mapped_column(String(50), nullable=False)
    input_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    output_response: Mapped[str] = mapped_column(Text, nullable=False)
    tokens_utilizados: Mapped[int] = mapped_column(Integer, nullable=True)
    executado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="historico")
