import cohere
import logging
from config.settings import settings
from typing import Optional
from fastapi import HTTPException

logger = logging.getLogger(__name__)

try:
    co = cohere.Client(settings.COHERE_API_KEY)
except Exception as e:
    logger.critical(f"Échec de l'initialisation du client Cohere: {str(e)}")
    raise HTTPException(
        status_code=500,
        detail="Service d'analyse de texte indisponible"
    )

def get_orientation_data(text: str) -> str:
    if not text or len(text.strip()) < 10:
        logger.warning(f"Texte d'entrée trop court: {len(text)} caractères")
        raise ValueError("Le texte d'entrée doit contenir au moins 10 caractères")

    prompt = f"""
    Analyse ce texte et extrais TOUTES les informations pertinentes avec précision.
    Réponds UNIQUEMENT avec un JSON valide en suivant STRICTEMENT sans rajouter un seul champ qui n'est pas mentionne a ce schéma :

    {{
        "firstName": "prénom ou null",
        "lastName": "nom ou null",
        "telephone": "numéro international ou null",
        "email": "email valide ou null",
        "preferredSubjects": "matières séparées par des virgules ou null",
        "fee": {{
            "formation": {{"min": "nombre (sans €) ou null", "max": "nombre ou null"}},
            "logement": {{"min": "nombre ou null", "max": "nombre ou null"}}
        }},
        "address": {{
            "city": "ville ou null",
            "region": "région/pays ou null", 
            "country": "pays ou null"
        }},
        "skills": "compétences séparées par des virgules ou null",
        "desiredFocus": "domaine spécifique ou null",
        "previousExperience": "expériences ou null"
    }}

    Règles CRITIQUES :
    1. Extrais TOUS les nombres pour les budgets (ignore les symboles €)
    2. Pour les coordonnées, garde uniquement les formats valides
    3. Nettoie les textes (pas de sauts de ligne, guillemets inutiles)
    4. Si une information est manquante, utilise null

    Texte à analyser : {text}
    """
    try:
        logger.info(f"Envoi d'une requête à Cohere - Taille du texte: {len(text)} caractères")
        response = co.generate(
            prompt=prompt,
            max_tokens=600,
            temperature=0.2
        )
        logger.debug(f"Réponse reçue - Premiers 200 caractères: {response.generations[0].text[:200]}...")
        return response.generations[0].text.strip()
    
    except cohere.CohereError as e:
        logger.error(f"Erreur Cohere: {str(e)} - Code: {e.http_status}")
        raise HTTPException(
            status_code=e.http_status or 502,
            detail=f"Erreur du service d'analyse: {e.message}"
        )
    except Exception as e:
        logger.critical(f"Erreur inattendue: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Erreur interne du serveur"
        )