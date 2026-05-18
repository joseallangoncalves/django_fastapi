from datetime import datetime
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

class TokenAcesso(Base):
    __tablename__ = "tokens_acesso"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    expira_em: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revogado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="tokens")
