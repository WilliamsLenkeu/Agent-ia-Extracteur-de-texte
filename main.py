import logging
from fastapi import FastAPI
from app.api.router import api_router
from config.security import add_cors_middleware
from config.settings import settings

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('api.log')  # Écrit aussi dans un fichier
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Orientation API",
    description="API pour l'orientation scolaire/professionnelle",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None
)

# Ajoutez ce middleware pour logger les requêtes
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Requête reçue: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"Réponse envoyée: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Erreur non gérée: {str(e)}", exc_info=True)
        raise

app = add_cors_middleware(app)
app.include_router(api_router, prefix="/api")