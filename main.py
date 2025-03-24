from fastapi import FastAPI
from app.api.router import api_router
from config.security import add_cors_middleware
from config.settings import settings

app = FastAPI(
    title="Orientation API",
    description="API ouverte pour l'orientation scolaire/professionnelle",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None
)

# Configuration CORS uniquement
app = add_cors_middleware(app)

# Inclusion des routes
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)