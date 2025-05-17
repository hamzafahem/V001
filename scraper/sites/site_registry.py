from typing import Dict, Type, Any
import importlib
import logging
from scraper.base.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

# Registre des scrapers disponibles
SCRAPER_REGISTRY = {
    "celio": "scraper.sites.celio_scraper.CelioScraper",
    "modov": "scraper.sites.modov_scraper.ModovScraper"
}

def get_scraper_class(site_type: str) -> Type[BaseScraper]:
    """
    Récupère la classe de scraper basée sur le type de site
    
    Args:
        site_type: Type de site (celio, modov, etc.)
        
    Returns:
        Classe de scraper
    """
    if site_type not in SCRAPER_REGISTRY:
        raise ValueError(f"Type de scraper non supporté: {site_type}")
    
    try:
        # Importer dynamiquement la classe
        module_path, class_name = SCRAPER_REGISTRY[site_type].rsplit('.', 1)
        module = importlib.import_module(module_path)
        scraper_class = getattr(module, class_name)
        return scraper_class
    except (ImportError, AttributeError) as e:
        logger.error(f"Erreur lors de l'importation du scraper {site_type}: {str(e)}")
        raise

def get_all_sites():
    """
    Récupère la liste de tous les sites supportés
    
    Returns:
        Liste des types de sites supportés
    """
    return list(SCRAPER_REGISTRY.keys())