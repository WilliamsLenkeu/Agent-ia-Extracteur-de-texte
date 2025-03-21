import cohere
import os
from dotenv import load_dotenv
import logging
import json
import re
from typing import Optional

# Charger les variables d'environnement
load_dotenv()

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Récupérer la clé API Cohere
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

if not COHERE_API_KEY:
    raise ValueError("La clé API de Cohere n'est pas définie dans le fichier .env")

# Initialisation du client Cohere
co = cohere.Client(COHERE_API_KEY)

def get_orientation_data(text: str) -> str:
    """Envoie un texte à Cohere et retourne la réponse générée."""
    prompt = f"""
    Analyse ce texte et extrait uniquement les informations suivantes en format JSON valide. 
    Ne réponds qu'avec ce format JSON, sans ajouter de texte supplémentaire.

    JSON :
    {{
        "firstName": null,
        "lastName": null,
        "preferredSubjects": null,
        "address": {{
            "city": null,
            "region": null,
            "country": null
        }},
        "skills": null,
        "telephone": null,
        "email": null,
        "fee": {{
            "formation": null,
            "logement": null
        }},
        "desiredFocus": null,
        "previousExperience": null
    }}

    Voici le texte à analyser : {text}
    """

    response = co.generate(prompt=prompt, max_tokens=300)
    result = response.generations[0].text.strip()
    logger.info(f"Réponse de Cohere : {result}")

    return result

def get_suggestions(question: str, infos: Optional[str] = None) -> list:
    """Génère une liste de suggestions en fonction de la question posée."""
    prompt = f"""
    Tu es un assistant spécialisé dans l'orientation scolaire et professionnelle.
    Réponds uniquement avec une liste de 6 suggestions pertinentes sous le format JSON suivant :
    
    {{"suggestions": ["réponse1", "réponse2", "réponse3", ..., "réponse10"]}}
    
    Question : "{question}"
    """

    if infos:
        prompt += f'\nInformations utilisateur : {infos}'

    response = co.generate(prompt=prompt, max_tokens=100)
    result_text = response.generations[0].text.strip()

    try:
        extracted_json = re.search(r"```json\n(.*?)\n```", result_text, re.DOTALL)
        if extracted_json:
            result_text = extracted_json.group(1)

        data = json.loads(result_text)
        return data.get("suggestions", [])

    except json.JSONDecodeError:
        logger.error(f"Erreur lors du parsing JSON des suggestions : {result_text}")
        return []

