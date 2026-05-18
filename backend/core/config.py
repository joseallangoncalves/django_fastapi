import os
from dotenv import load_dotenv

# Load .env file specifically resolving backend/ directory path
from pathlib import Path
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

class Settings:
    PROJECT_NAME: str = "Aula - API de IA e Gestão de Usuários"
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-for-jwt-signing-1234567890")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Internal communication API token between Django and FastAPI
    API_TOKEN: str = os.getenv("API_TOKEN", "123")
    
    # Database URL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./pos_sistema.db")

settings = Settings()
