import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class Config:
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# Vérification de la clé API
if not Config.COHERE_API_KEY:
    raise ValueError("La clé API de Cohere est manquante dans le fichier .env")
