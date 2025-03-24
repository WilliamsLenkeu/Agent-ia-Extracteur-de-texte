from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings

def add_cors_middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS.split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app