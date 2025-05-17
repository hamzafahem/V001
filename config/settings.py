import os
from typing import Dict, List, Union

# Configuration simple sans classes Pydantic
class Settings:
    # Application
    APP_NAME = "EAN Scraper Service"
    DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
    SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-change-in-production")
    API_PREFIX = "/api"
    UPLOAD_FOLDER = "static/uploads"
    
    # Base de données
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///ean_results.db")
    
    # Images
    MAX_IMAGES_PER_PRODUCT = int(os.environ.get("MAX_IMAGES_PER_PRODUCT", "3"))
    ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"]
    MAX_FILE_SIZE_MB = 5
    IMAGE_STORAGE_PATH = "static/product_images"
    
    # Configuration du scraper
    REQUEST_TIMEOUT = 10
    
    # Sites
    CELIO_SITES = [
        {"base_url": "https://www.celiostore.cz/hledat", "country": "République Tchèque", "site_name": "celiostore.cz", "param": "query"},
        {"base_url": "https://www.celiostore.sk/hladat", "country": "Slovaquie", "site_name": "celiostore.sk", "param": "query"},
        {"base_url": "https://www.celio.tn/search", "country": "Tunisie", "site_name": "celio.tn", "param": "q"},
        {"base_url": "https://www.celio.it/cerca", "country": "Italie", "site_name": "celio.it", "param": "q"}
    ]
    
    MODOV_DOMAINS = [
        {'domain': 'modov.sk', 'priority': 1, 'country': 'SK'},
        {'domain': 'zbozi.cz', 'priority': 2, 'country': 'CZ'},
        {'domain': 'hledejceny.cz', 'priority': 3, 'country': 'CZ'},
        {'domain': 'arukereso.hu', 'priority': 4, 'country': 'HU'},
        {'domain': 'ceneo.pl', 'priority': 5, 'country': 'PL'},
        {'domain': 'idealo.de', 'priority': 6, 'country': 'DE'}
    ]
    
    # Headers HTTP
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # Propriétés pour maintenir la compatibilité avec l'ancienne structure
    @property
    def database(self):
        return type("DatabaseSettings", (), {"url": self.DATABASE_URL})
    
    @property
    def image(self):
        return type("ImageSettings", (), {
            "max_images_per_product": self.MAX_IMAGES_PER_PRODUCT,
            "allowed_extensions": self.ALLOWED_EXTENSIONS,
            "max_file_size_mb": self.MAX_FILE_SIZE_MB,
            "storage_path": self.IMAGE_STORAGE_PATH
        })
    
    @property
    def scraper(self):
        return type("ScraperSettings", (), {
            "celio_sites": self.CELIO_SITES,
            "modov_domains": self.MODOV_DOMAINS,
            "request_timeout": self.REQUEST_TIMEOUT
        })
    
    @property
    def database_url(self):
        """Pour compatibilité avec le code existant"""
        return self.DATABASE_URL

# Charger les variables d'environnement depuis .env si le fichier existe
env_file = ".env"
if os.path.exists(env_file):
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                key, value = line.split("=", 1)
                os.environ[key] = value
            except ValueError:
                pass

# Créer une instance des paramètres
settings = Settings()