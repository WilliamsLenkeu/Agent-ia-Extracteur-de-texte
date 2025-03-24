# Ancien (ne fonctionne plus) :
# from pydantic import BaseSettings

# Nouveau :
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    COHERE_API_KEY: str
    ALLOWED_ORIGINS: str = "*"
    
    class Config:
        env_file = ".env"

settings = Settings()