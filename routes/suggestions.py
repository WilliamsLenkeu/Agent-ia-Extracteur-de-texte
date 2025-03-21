from fastapi import APIRouter, HTTPException
from models.suggestions import SuggestionRequest, SuggestionResponse
from services.cohere_service import get_suggestions
import re
import logging

router = APIRouter()

# Configuration du logger
logger = logging.getLogger(__name__)

@router.post("/get-suggestions", response_model=SuggestionResponse)
async def get_suggestions_route(request: SuggestionRequest):
    """Endpoint pour obtenir des suggestions basées sur une question donnée."""
    try:
        suggestions = get_suggestions(request.question, request.infos)
        return SuggestionResponse(suggestions=suggestions)

    except Exception as e:
        logger.error(f"Erreur dans /get-suggestions : {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la génération des suggestions.")
