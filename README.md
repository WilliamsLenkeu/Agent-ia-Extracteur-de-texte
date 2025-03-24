# MonAgent

**MonAgent** est un agent IA conçu pour extraire et structurer des informations à partir de textes bruts. Il est particulièrement utile pour l'extraction de données telles que les noms, les numéros de téléphone, les adresses e-mail, les budgets, et bien plus encore. Cet agent utilise l'API Cohere pour le traitement du langage naturel (NLP) et FastAPI pour exposer les fonctionnalités via une API REST.

---

## Fonctionnalités

- Extraction de données structurées à partir de textes bruts.
- Support pour les informations personnelles (noms, téléphones, e-mails).
- Extraction de budgets (formation, logement).
- Structuration des données en JSON.
- API REST facile à utiliser.

---

## Prérequis

- Python 3.8 ou supérieur.
- Un fichier `.env` contenant votre clé API Cohere.

---

## Installation

1. Clonez ce dépôt

2. Créez un environnement virtuel (recommandé) :

   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows : venv\Scripts\activate
   ```

3. Installez les dépendances :

   ```bash
   pip install -r requirements.txt
   ```

4. Configurez votre fichier `.env` :

   Créez un fichier `.env` à la racine du projet et ajoutez-y votre clé API Cohere :

   ```plaintext
   COHERE_API_KEY=votre_clé_api_cohere_ici
   ```

---

## Utilisation

### Lancer l'API

Pour démarrer l'API en mode développement avec rechargement automatique :

```bash
uvicorn main:app --reload
```

L'API sera disponible à l'adresse locale : `http://127.0.0.1:8000`

Pour rendre l'API accessible sur votre réseau local (par exemple pour la tester depuis un autre appareil) :

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Dans ce cas, l'API sera accessible :
- Localement : `http://127.0.0.1:8000`
- Sur le réseau local via l'adresse IP de votre machine

#### Comment trouver votre adresse IP locale :
- **Windows** : Exécutez `ipconfig` dans l'invite de commandes et cherchez "IPv4 Address"
- **macOS/Linux** : Exécutez `ifconfig` (ou `ip a` sur certaines distributions) et cherchez "inet" (souvent sous wlan0 pour WiFi ou eth0 pour Ethernet)

Par exemple, si votre adresse IP est `192.168.1.20`, l'API sera accessible via : `http://192.168.1.20:8000`

> **Important** : Pour des raisons de sécurité, ne partagez pas cette adresse en dehors de votre réseau local et n'utilisez pas ce mode en production.

### Tester l'agent

Vous pouvez tester l'agent en envoyant une requête POST à l'endpoint `/process-text` avec un texte brut. Voici un exemple utilisant `curl` :

```bash
curl -X POST "http://127.0.0.1:8000/process-text" \
-H "Content-Type: application/json" \
-d '{
  "text": "Je m\'appelle Léa Martin et je suis passionnée par les sciences de l\'environnement. Mon numéro de téléphone est +33 6 12 34 56 78, et mon e-mail est lea.martin@example.com. Mon budget pour une formation est de 5000 à 7000 €."
}'
```

### Exemple de réponse

```json
{
  "firstName": "Léa",
  "lastName": "Martin",
  "telephone": "+33 6 12 34 56 78",
  "email": "lea.martin@example.com",
  "preferredSubjects": "sciences de l'environnement",
  "fee": {
    "formation": {"min": 5000, "max": 7000},
    "logement": {"min": null, "max": null}
  },
  "address": {
    "city": null,
    "region": null,
    "country": null
  },
  "skills": null,
  "desiredFocus": null,
  "previousExperience": null
}
```

---

## Structure du projet

- `main.py` : Point d'entrée de l'application FastAPI.
- `requirements.txt` : Liste des dépendances Python.
- `.env` : Fichier de configuration pour les variables d'environnement.
- `README.md` : Ce fichier.

---

## Dépendances

Les dépendances du projet sont listées dans `requirements.txt`. Voici les principales :

- `fastapi` : Framework pour construire l'API.
- `uvicorn` : Serveur ASGI pour exécuter FastAPI.
- `cohere` : Client pour l'API Cohere.
- `python-dotenv` : Pour charger les variables d'environnement depuis un fichier `.env`.
- `pydantic` : Pour la validation des données.

---

## Tests

Pour tester l'agent, vous pouvez utiliser des outils comme `curl`, `Postman`, ou écrire des tests unitaires avec `pytest`.

### Exemple de test unitaire

Créez un fichier `test_main.py` :

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_process_text():
    response = client.post(
        "/process-text",
        json={
            "text": "Je m'appelle Léa Martin. Mon budget est de 5000 à 7000 €."
        },
    )
    assert response.status_code == 200
    assert response.json()["firstName"] == "Léa"
    assert response.json()["fee"]["formation"] == {"min": 5000, "max": 7000}
```

Exécutez les tests :

```bash
pytest
```

---

## Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Forkez le projet.
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/nouvelle-fonctionnalité`).
3. Committez vos changements (`git commit -m 'Ajouter une nouvelle fonctionnalité'`).
4. Pushez la branche (`git push origin feature/nouvelle-fonctionnalité`).
5. Ouvrez une Pull Request.
