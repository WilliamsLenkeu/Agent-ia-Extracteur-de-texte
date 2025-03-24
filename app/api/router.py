from fastapi import APIRouter
from .endpoints import orientation

api_router = APIRouter()

api_router.include_router(
    orientation.router,
    prefix="/orientation",
    tags=["Orientation"]
)