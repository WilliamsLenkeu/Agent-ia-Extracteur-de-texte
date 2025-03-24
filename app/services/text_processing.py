import re
import json
import logging
from typing import Dict, Optional  # Ajout de Optional ici

logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    logger.debug(f"Nettoyage du texte original: {text[:100]}...")
    cleaned = text.strip().replace("\n", " ")
    cleaned = re.sub(r'\s+', ' ', cleaned)
    logger.debug(f"Texte nettoyé: {cleaned[:100]}...")
    return cleaned

def extract_budgets(budget_str: str) -> Dict[str, Optional[int]]:
    if not budget_str:
        return {"min": None, "max": None}
    
    # Extraction améliorée des nombres (ignore €, k, etc.)
    numbers = [int(num) for num in re.findall(r'\b\d+\b', str(budget_str))]
    
    if len(numbers) >= 2:
        return {"min": min(numbers), "max": max(numbers)}
    elif numbers:
        return {"min": numbers[0], "max": numbers[0]}
    return {"min": None, "max": None}

def parse_cohere_response(response_text: str) -> dict:
    try:
        logger.debug(f"Parsing de la réponse: {response_text[:200]}...")
        # Extraction plus robuste du JSON
        json_str = re.search(r'\{.*\}', response_text, re.DOTALL)
        if not json_str:
            raise ValueError("No JSON found in response")
            
        data = json.loads(json_str.group(0))
        
        # Normalisation des nombres
        if 'fee' in data:
            data['fee'] = {
                "formation": extract_budgets(data['fee'].get('formation')),
                "logement": extract_budgets(data['fee'].get('logement'))
            }
        
        # Nettoyage des chaînes de caractères
        for field in ['firstName', 'lastName', 'preferredSubjects', 'skills']:
            if field in data and data[field]:
                data[field] = data[field].strip().replace('"', '')
        
        logger.info(f"Parsing réussi: {json.dumps(data, indent=2)}")
        return data
    except Exception as e:
        logger.error(f"Erreur de parsing: {str(e)} - Réponse originale: {response_text[:500]}", exc_info=True)
        return {}