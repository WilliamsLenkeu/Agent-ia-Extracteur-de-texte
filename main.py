from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
import cohere
import json
import re
import logging
from dotenv import load_dotenv
import os

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupérer la clé API de Cohere depuis les variables d'environnement
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# Vérifier si la clé API est bien définie
if not COHERE_API_KEY:
    raise ValueError("La clé API de Cohere n'est pas définie dans le fichier .env")

# Initialisation du client Cohere avec la clé API
co = cohere.Client(COHERE_API_KEY)

# Création de l'application FastAPI
app = FastAPI()

# Configurer les logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modèle de données représentant le profil d'orientation
class OrientationProfile(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    preferredSubjects: Optional[str] = None
    fee: Dict[str, Dict[str, Optional[int]]] = {"formation": {"min": None, "max": None}, "logement": {"min": None, "max": None}}
    address: Dict[str, Optional[str]] = {"city": None, "region": None, "country": None}
    skills: Optional[str] = None
    desiredFocus: Optional[str] = None
    previousExperience: Optional[str] = None

# Modèle pour la réception de texte brut
class TextInput(BaseModel):
    text: str

# 🔹 Fonction pour nettoyer le texte
def clean_text(text: str) -> str:
    text = text.strip().replace("\n", " ")
    text = re.sub(r'\s+', ' ', text)
    return text

# 🔹 Fonction pour extraire les informations de budget
def extract_budgets(budget_str: str) -> Dict[str, Optional[int]]:
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

# 📝 Endpoint principal pour traiter le texte et extraire le profil d'orientation
@app.post("/process-text", response_model=OrientationProfile)
async def process_text(input: TextInput):
    try:
        # Nettoyage du texte d'entrée
        text = clean_text(input.text)
        logger.info(f"Texte nettoyé : {text}")

        # 🔹 Construction du prompt pour Cohere avec une sortie JSON stricte
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

        # 🔹 Appel à Cohere pour générer une réponse
        response = co.generate(prompt=prompt, max_tokens=300)
        logger.info(f"Réponse de l'IA : {response.generations[0].text.strip()}")

        extracted_info = response.generations[0].text.strip()

        # 🔹 Extraction sécurisée du JSON
        extracted_json = re.search(r"```json\n(.*?)\n```", extracted_info, re.DOTALL)
        if extracted_json:
            extracted_info = extracted_json.group(1)

        # 🔹 Conversion en JSON
        profile_data = json.loads(extracted_info)

        # 🔹 Extraction des budgets formation et logement
        formation_budget = extract_budgets(profile_data.get("fee", {}).get("formation"))
        logement_budget = extract_budgets(profile_data.get("fee", {}).get("logement"))

        # 🔹 Création du profil avec les données extraites
        profile = OrientationProfile(
            firstName=profile_data.get("firstName"),
            lastName=profile_data.get("lastName"),
            telephone=profile_data.get("telephone"),
            email=profile_data.get("email"),
            preferredSubjects=profile_data.get("preferredSubjects"),
            fee={"formation": formation_budget, "logement": logement_budget},
            address=profile_data.get("address", {"city": None, "region": None, "country": None}),
            skills=profile_data.get("skills"),
            desiredFocus=profile_data.get("desiredFocus"),
            previousExperience=profile_data.get("previousExperience"),
        )

        return profile

    except json.JSONDecodeError as e:
        logger.error(f"Erreur lors de la conversion en JSON : {e}")
        raise HTTPException(status_code=500, detail="Erreur dans l'analyse JSON de la réponse de Cohere.")
    except Exception as e:
        logger.error(f"Une erreur inattendue est survenue : {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 🔹 Exécution locale de l'API
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
