from fastapi import APIRouter, HTTPException
from models.orientation import OrientationProfile
from models.requests import TextInput
from services.cohere_service import get_orientation_data
from services.text_processing import clean_text, parse_cohere_response
import logging

# Configuration du logger
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/process-text", response_model=OrientationProfile)
async def process_text(input: TextInput):
    """Endpoint pour analyser un texte et extraire un profil d'orientation."""
    try:
        text = clean_text(input.text)
        logger.info(f"Texte nettoyé : {text}")

        cohere_response = get_orientation_data(text)
        profile_data = parse_cohere_response(cohere_response)

        return OrientationProfile(**profile_data)

    except Exception as e:
        logger.error(f"Erreur dans /process-text : {e}")
        raise HTTPException(status_code=500, detail=str(e))
