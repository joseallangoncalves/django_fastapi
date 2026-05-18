# Compatibility layer for database imports as defined in spec/02_banco_de_dados_usuarios.md
from db.connection import engine, SessionLocal
from models.base import Base
from db.dependency import get_db

__all__ = ["engine", "SessionLocal", "Base", "get_db"]
