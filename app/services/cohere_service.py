import cohere
import logging
from config.settings import settings
from typing import Optional

logger = logging.getLogger(__name__)
co = cohere.Client(settings.COHERE_API_KEY)

def get_orientation_data(text: str) -> str:
    prompt = f"""
    Analyse ce texte et extrais TOUTES les informations pertinentes avec précision.
    Réponds UNIQUEMENT avec un JSON valide en suivant STRICTEMENT ce schéma :

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
        response = co.generate(
            prompt=prompt,
            max_tokens=600,  # Augmenté pour les longs textes
            temperature=0.2  # Plus précis
        )
        return response.generations[0].text.strip()
    except Exception as e:
        logger.error(f"Cohere error: {str(e)}")
        raise