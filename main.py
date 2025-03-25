import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.router import api_router
from config.settings import settings
import asyncio

# Configuration du logging
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
    title="API Extraction Texte",
    description="API pour l'extraction de texte depuis documents et images",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
    timeout=300  # 5 minutes timeout global
)

@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    """Middleware de timeout global"""
    try:
        return await call_next(request)
    except asyncio.TimeoutError:
        logger.error("Timeout global atteint")
        return JSONResponse(
            status_code=504,
            content={"detail": "Timeout du serveur"}
        )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Gestion des erreurs HTTP"""
    logger.warning(
        f"Erreur {exc.status_code} pour {request.method} {request.url}: {exc.detail}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Gestion des autres exceptions"""
    logger.error(
        f"Erreur inattendue pour {request.method} {request.url}",
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Erreur interne du serveur"},
    )

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router principal
app.include_router(api_router, prefix="/api")

@app.on_event("startup")
async def startup():
    """Actions au démarrage"""
    logger.info("Démarrage de l'API")
    # Vérification des dépendances
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
    except Exception:
        logger.critical("Tesseract OCR n'est pas installé correctement")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)