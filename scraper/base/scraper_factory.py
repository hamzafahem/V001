from typing import Dict, Any, Optional
import logging
from scraper.sites.site_registry import get_scraper_class

logger = logging.getLogger(__name__)

class ScraperFactory:
    """Factory pour créer des instances de scrapers"""
    
    @staticmethod
    def get_scraper(site_type: str, site_config: Dict[str, Any]):
        """
        Crée une instance de scraper basée sur le type de site
        
        Args:
            site_type: Type de site (celio, modov, etc.)
            site_config: Configuration du site
            
        Returns:
            Instance de scraper
        """
        try:
            scraper_class = get_scraper_class(site_type)
            return scraper_class(site_config)
        except Exception as e:
            logger.error(f"Erreur lors de la création du scraper {site_type}: {str(e)}")
            raise ValueError(f"Type de scraper non supporté: {site_type}")

# Instance singleton
scraper_factory = ScraperFactory()