from datetime import datetime
from sqlalchemy import Integer, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    cargo: Mapped[str] = mapped_column(String(20), default="user", nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    tokens: Mapped[list["TokenAcesso"]] = relationship("TokenAcesso", back_populates="usuario", cascade="all, delete-orphan")
    historico: Mapped[list["HistoricoAgente"]] = relationship("HistoricoAgente", back_populates="usuario")
    contratos: Mapped[list["Contrato"]] = relationship("Contrato", back_populates="usuario", cascade="all, delete-orphan")
