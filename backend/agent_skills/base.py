from groq import Groq
from core.config import settings

# Central Groq client initialization
# If API key is empty, we will handle it gracefully or raise an error in skills.
client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None
