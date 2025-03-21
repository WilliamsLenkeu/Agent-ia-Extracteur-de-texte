from fastapi import FastAPI
from routes import profile, suggestions
import logging

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Création de l'application FastAPI
app = FastAPI(title="API Orientation", description="Analyse de texte pour l'orientation scolaire")

# Inclusion des routes
app.include_router(profile.router)
app.include_router(suggestions.router)

# Point d'entrée pour exécuter l'API
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
