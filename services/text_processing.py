import re
import json
import logging

# Configuration du logger
logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """Nettoie le texte en supprimant les espaces superflus."""
    text = text.strip().replace("\n", " ")
    text = re.sub(r'\s+', ' ', text)
    return text

def extract_budgets(budget_str: str) -> dict:
    """Extrait les valeurs minimales et maximales du budget à partir d'une chaîne de caractères."""
    if not budget_str:
        return {"min": None, "max": None}

    budget_values = re.findall(r'\d+', budget_str)
    if len(budget_values) >= 2:
        min_budget = int(budget_values[0])
        max_budget = int(budget_values[1])
    elif len(budget_values) == 1:
        min_budget = int(budget_values[0])
        max_budget = int(budget_values[0])
    else:
        min_budget, max_budget = None, None

    return {"min": min_budget, "max": max_budget}

def parse_cohere_response(response_text: str) -> dict:
    """Convertit la réponse de Cohere en JSON structuré."""
    try:
        extracted_json = re.search(r"```json\n(.*?)\n```", response_text, re.DOTALL)
        if extracted_json:
            response_text = extracted_json.group(1)

        profile_data = json.loads(response_text)

        # Extraction des budgets
        profile_data["fee"] = {
            "formation": extract_budgets(profile_data.get("fee", {}).get("formation")),
            "logement": extract_budgets(profile_data.get("fee", {}).get("logement"))
        }

        return profile_data
    except json.JSONDecodeError as e:
        logger.error(f"Erreur JSON : {e}")
        return {}
