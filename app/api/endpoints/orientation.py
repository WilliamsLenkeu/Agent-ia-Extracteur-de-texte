import json
import logging
from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import OrientationProfile
from app.models.requests import TextInput
from app.services.cohere_service import get_orientation_data
from app.services.text_processing import clean_text, parse_cohere_response

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/process-text", response_model=OrientationProfile)
async def process_text(input: TextInput):
    try:
        logger.info(f"Début du traitement - Taille du texte: {len(input.text)} caractères")
        
        text = clean_text(input.text)
        if len(text) < 10:
            logger.warning("Texte nettoyé trop court")
            raise HTTPException(400, detail="Le texte doit contenir au moins 10 caractères valides")
        
        cohere_response = get_orientation_data(text)
        profile_data = parse_cohere_response(cohere_response)
        
        if not profile_data:
            logger.error("Échec du parsing de la réponse Cohere")
            raise HTTPException(422, detail="Impossible d'analyser la réponse de l'IA")
        
        logger.info("Traitement réussi")
        return OrientationProfile(**profile_data)
        
    except HTTPException:
        raise  # On laisse passer les HTTPException intentionnelles
    except json.JSONDecodeError as e:
        logger.error(f"Erreur JSON: {str(e)}")
        raise HTTPException(422, detail="Format de données invalide")
    except Exception as e:
        logger.critical(f"Erreur critique: {str(e)}", exc_info=True)
        raise HTTPException(500, detail="Échec du traitement")