from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
import cohere
import json
import re
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()

# Récupérer la clé API de Cohere
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
if not COHERE_API_KEY:
    raise ValueError("La clé API de Cohere n'est pas définie dans le fichier .env")

# Initialisation du client Cohere
co = cohere.Client(COHERE_API_KEY)

# Initialisation de FastAPI
app = FastAPI()

# Modèle de données du profil d'orientation
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

# 🔹 Fonction pour extraire les budgets sous forme numérique
def extract_budgets(budget_str: str) -> Dict[str, Optional[int]]:
    if not budget_str:
        return {"min": None, "max": None}

    # Vérifier si le budget est une plage
    if 'to' in budget_str or '-' in budget_str:
        # Extraire les deux nombres et les convertir en entiers
        budget_values = re.findall(r'\d+', budget_str)
        if len(budget_values) == 2:
            return {"min": int(budget_values[0]), "max": int(budget_values[1])}
    
    # Si ce n'est pas une plage, tenter de convertir un seul nombre
    budget_values = re.findall(r'\d+', budget_str)
    if budget_values:
        return {"min": int(budget_values[0]), "max": int(budget_values[0])}
    
    return {"min": None, "max": None}

# 🔹 Fonction pour nettoyer la réponse brute de Cohere
def clean_response(response: str) -> str:
    # Enlever les retours à la ligne et espaces inutiles
    response = response.replace("\n", " ").strip()
    return response

# 🔹 Fonction pour valider et convertir la réponse en JSON
def validate_json(response: str):
    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        print(f"❌ Erreur JSON: {e}")
        raise HTTPException(status_code=500, detail="Erreur dans le format JSON de la réponse de Cohere.")

# 📝 Endpoint principal pour traiter le texte et extraire le profil d'orientation
@app.post("/process-text", response_model=OrientationProfile)
async def process_text(input: TextInput):
    try:
        # Nettoyage du texte
        text = clean_text(input.text)

        # 🔹 Construction du prompt pour Cohere
        prompt = f"""
        Analyse ce texte et extrait uniquement les informations suivantes en format JSON, sans ajouter de texte explicatif :
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

        Si une information est absente, laisse `null` à la place.  
        Voici le texte à analyser : {text}
        """

        # Appel à Cohere
        response = co.generate(prompt=prompt, max_tokens=200)
        extracted_info = response.generations[0].text.strip()

        # 📌 Log uniquement la réponse brute de l'IA
        print("📥 Réponse brute de Cohere avant nettoyage :", extracted_info)

        # Nettoyer la réponse brute avant de la convertir en JSON
        cleaned_response = clean_response(extracted_info)

        # 📌 Log de la réponse nettoyée
        print("📥 Réponse brute de Cohere après nettoyage :", cleaned_response)

        # Valider et convertir la réponse nettoyée en JSON
        profile_data = validate_json(cleaned_response)

        # Création du profil d'orientation
        profile = OrientationProfile(
            firstName=profile_data.get("firstName"),
            lastName=profile_data.get("lastName"),
            telephone=profile_data.get("telephone"),
            email=profile_data.get("email"),
            preferredSubjects=profile_data.get("preferredSubjects"),
            fee={
                "formation": extract_budgets(profile_data.get("fee", {}).get("formation")),
                "logement": extract_budgets(profile_data.get("fee", {}).get("logement"))
            },
            address=profile_data.get("address", {"city": None, "region": None, "country": None}),
            skills=profile_data.get("skills"),
            desiredFocus=profile_data.get("desiredFocus"),
            previousExperience=profile_data.get("previousExperience"),
        )

        return profile

    except Exception as e:
        print("❌ Une erreur inattendue est survenue :", e)
        raise HTTPException(status_code=500, detail=str(e))

# 🔹 Exécution locale
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
