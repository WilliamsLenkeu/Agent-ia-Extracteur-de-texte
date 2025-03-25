from fastapi import APIRouter
from .endpoints import orientation, text_extraction

api_router = APIRouter()

api_router.include_router(
    orientation.router,
    prefix="/orientation",
    tags=["Orientation"]
)

api_router.include_router(
    text_extraction.router,
    prefix="/text-extraction",
    tags=["Text Extraction"]
)
