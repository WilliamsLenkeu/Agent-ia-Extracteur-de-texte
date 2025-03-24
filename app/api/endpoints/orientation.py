import json
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
        logger.info(f"Début du traitement pour le texte: {input.text[:50]}...")  # Log les 50 premiers caractères
        
        text = clean_text(input.text)
        logger.debug(f"Texte nettoyé: {text[:100]}...")  # Log debug pour le texte nettoyé
        
        cohere_response = get_orientation_data(text)
        logger.debug(f"Réponse brute de Cohere: {cohere_response[:200]}...")  # Log les 200 premiers caractères
        
        profile_data = parse_cohere_response(cohere_response)
        logger.info(f"Données parsées avec succès: {json.dumps(profile_data, indent=2)}")
        
        return OrientationProfile(**profile_data)
        
    except json.JSONDecodeError as e:
        logger.error(f"Erreur de décodage JSON: {str(e)} - Réponse de Cohere: {cohere_response[:500]}", exc_info=True)
        raise HTTPException(422, "Invalid data format from AI")
    except HTTPException:
        raise  # On ne logge pas les HTTPException intentionnelles
    except Exception as e:
        logger.critical(f"Erreur critique lors du traitement: {str(e)}", exc_info=True)
        raise HTTPException(500, "Processing failed")