from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseScraper(ABC):
    """Classe de base abstraite pour tous les scrapers"""
    
    def __init__(self, site_config: Dict[str, Any]):
        """Initialise le scraper avec la configuration du site"""
        self.site_config = site_config
    
    @abstractmethod
    async def scrape_ean(self, ean: str, brand: Optional[str] = None) -> Dict[str, Any]:
        """
        Scrape les informations d'un produit à partir d'un EAN
        
        Args:
            ean: Code EAN à scraper
            brand: Marque du produit (optionnel)
            
        Returns:
            Dict contenant les informations du produit
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nom du scraper"""
        pass