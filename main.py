from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
import cohere
import json
import re
from dotenv import load_dotenv
import os
import inflect
import word2number.w2n as w2n

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

# 🔹 Fonction pour convertir un texte en nombre
def text_to_number(text: str) -> int:
    try:
        return w2n.word_to_num(text.lower())
    except ValueError:
        return None  # Retourne None si la conversion échoue

# 🔹 Fonction pour extraire les budgets même s'ils sont en lettres
def extract_budgets(budget_str: str) -> Dict[str, Optional[int]]:
    if not budget_str:
        return {"min": None, "max": None}

    # Extraction des nombres sous forme numérique
    budget_values = re.findall(r'\d+', budget_str)

    # Extraction des nombres écrits en lettres
    words_numbers = re.findall(r'([a-zA-Z\s-]+)', budget_str)
    for word in words_numbers:
        num = text_to_number(word)
        if num is not None:
            budget_values.append(str(num))

    # Conversion en entier
    budget_values = [int(value) for value in budget_values]

    if len(budget_values) >= 2:
        return {"min": min(budget_values), "max": max(budget_values)}
    elif len(budget_values) == 1:
        return {"min": budget_values[0], "max": budget_values[0]}
    else:
        return {"min": None, "max": None}

# 📝 Endpoint principal pour traiter le texte et extraire le profil d'orientation
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
        print("📥 Réponse brute de Cohere :", extracted_info)

        # Conversion de la réponse JSON
        profile_data = json.loads(extracted_info)

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

    except json.JSONDecodeError as e:
        print("❌ Erreur lors de la conversion en JSON :", e)
        raise HTTPException(status_code=500, detail="Erreur dans l'analyse JSON de la réponse de Cohere.")
    except Exception as e:
        print("❌ Une erreur inattendue est survenue :", e)
        raise HTTPException(status_code=500, detail=str(e))

# 🔹 Exécution locale
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
