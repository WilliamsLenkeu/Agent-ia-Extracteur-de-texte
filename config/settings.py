from pydantic_settings import BaseSettings
import logging
from pydantic import validator

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    COHERE_API_KEY: str
    ALLOWED_ORIGINS: str = "*"
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

    @validator('COHERE_API_KEY', pre=True)
    def validate_api_key(cls, v):
        if not v:
            logger.critical("La clé API Cohere est manquante dans le fichier .env")
            raise ValueError("COHERE_API_KEY est requise")
        return v

settings = Settings()