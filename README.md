# MonAgent

**MonAgent** est un agent IA conçu pour extraire et structurer des informations à partir de textes bruts. Il est particulièrement utile pour l'extraction de données telles que les noms, les numéros de téléphone, les adresses e-mail, les budgets, et bien plus encore. Cet agent utilise l'API Cohere pour le traitement du langage naturel (NLP) et FastAPI pour exposer les fonctionnalités via une API REST.

---

## Fonctionnalités

- Extraction de données structurées à partir de textes bruts.
- Support pour les informations personnelles (noms, téléphones, e-mails).
- Extraction de budgets (formation, logement).
- Structuration des données en JSON.
- API REST facile à utiliser.
- Évolutivité : ajout futur de nouvelles tâches et capacités.

---

## Prérequis

- Python 3.8 ou supérieur.
- Un fichier `.env` contenant votre clé API Cohere.

---

## Installation

1. Clonez ce dépôt :
   ```bash
   git clone https://github.com/votre-repo/monagent.git
   cd monagent
   ```

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

---

## Dépendances

Les dépendances du projet sont listées dans `requirements.txt`. Voici les principales :

- `fastapi` : Framework pour construire l'API.
- `uvicorn` : Serveur ASGI pour exécuter FastAPI.
- `cohere` : Client pour l'API Cohere.
- `python-dotenv` : Pour charger les variables d'environnement depuis un fichier `.env`.
- `pydantic` : Pour la validation des données.
- `python-jose` : Gestion des JWT pour l'authentification (prévu pour des fonctionnalités futures).
- `passlib` : Utilisé pour le hachage sécurisé des mots de passe (prévu pour des fonctionnalités futures).
- `pydantic_settings` : Gestion avancée des paramètres de configuration.

---

## Évolutivité

MonAgent est conçu pour évoluer avec le temps. De nouvelles tâches et fonctionnalités seront ajoutées, comme :
- L'extraction avancée de compétences et d'expériences professionnelles.
- La suggestion automatique de formations et d'emplois.
- L'intégration avec d'autres API pour enrichir les recommandations.
- Un mécanisme d'authentification et de gestion des utilisateurs.

---

## Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Forkez le projet.
2. Créez une branche pour votre fonctionnalité :
   ```bash
   git checkout -b feature/nouvelle-fonctionnalité
   ```
3. Committez vos changements :
   ```bash
   git commit -m 'Ajouter une nouvelle fonctionnalité'
   ```
4. Pushez la branche :
   ```bash
   git push origin feature/nouvelle-fonctionnalité
   ```
5. Ouvrez une Pull Request.

---

Ce projet est en constante évolution, et votre aide est précieuse pour le rendre encore plus performant ! 🚀

