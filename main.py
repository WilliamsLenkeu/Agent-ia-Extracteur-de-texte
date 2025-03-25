import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api.router import api_router
from config.security import add_cors_middleware
from config.settings import settings

# Configuration avancée du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('api.log', encoding='utf-8')
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

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Requête {request.method} {request.url} - Client: {request.client.host}")
    try:
        response = await call_next(request)
        logger.info(f"Réponse {request.method} {request.url} - Statut: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Erreur pour {request.method} {request.url}: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Erreur interne du serveur"}
        )

# Gestion centralisée des exceptions
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    logger.warning(f"Erreur de validation: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

app = add_cors_middleware(app)
app.include_router(api_router, prefix="/api")

# Log au démarrage
logger.info("L'API a démarré avec succès")