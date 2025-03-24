import json  # Ajouter cette ligne en haut du fichier
import logging
from fastapi import APIRouter, HTTPException
from app.models.schemas import OrientationProfile
from app.models.requests import TextInput
from app.services.cohere_service import get_orientation_data
from app.services.text_processing import clean_text, parse_cohere_response

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/process-text", response_model=OrientationProfile)
async def process_text(input: TextInput):
    try:
        text = clean_text(input.text)
        logger.info(f"Processing text (length: {len(text)})")
        
        cohere_response = get_orientation_data(text)
        logger.debug(f"Raw Cohere response: {cohere_response[:200]}...")
        
        profile_data = parse_cohere_response(cohere_response)
        logger.debug(f"Parsed data: {profile_data}")
        
        return OrientationProfile(**profile_data)
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        raise HTTPException(422, "Invalid data format from AI")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(500, "Processing failed")