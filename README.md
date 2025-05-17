# Scraper-MService

Service de scraping pour les produits basé sur les codes EAN.

## Installation

1. Créer un environnement virtuel :
```bash
python -m venv venv
```

2. Activer l'environnement virtuel :
- Windows :
```bash
.\venv\Scripts\activate
```
- Linux/Mac :
```bash
source venv/bin/activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Initialiser le service :
```bash
python init_setup.py
```

## Démarrage

```bash
python main.py
```

Le service sera accessible sur `http://localhost:8000`

## Documentation API

- Swagger UI : `http://localhost:8000/docs`
- ReDoc : `http://localhost:8000/redoc`

## Endpoints principaux

- `/api/scraper/ean` : Scraper un EAN
- `/api/scraper/box` : Scraper des données de box
- `/api/upload/{ean}` : Upload d'images
- `/api/export` : Export de données
- `/api/health` : Vérification de l'état du service

## Configuration

La configuration se fait via le fichier `.env` :
- `DEBUG` : Mode debug (True/False)
- `SECRET_KEY` : Clé secrète pour l'application
- `DATABASE_URL` : URL de la base de données
- `MAX_IMAGES_PER_PRODUCT` : Nombre maximum d'images par produit 