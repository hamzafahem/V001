from typing import Dict, Any, Optional
import logging
import re
import aiohttp
from bs4 import BeautifulSoup

from scraper.base.base_scraper import BaseScraper
from config.settings import settings

logger = logging.getLogger(__name__)

class CelioScraper(BaseScraper):
    """Scraper pour les sites CELIO"""
    
    @property
    def name(self) -> str:
        return "CELIO"
    
    async def scrape_ean(self, ean: str, brand: Optional[str] = None) -> Dict[str, Any]:
        """Scrape les informations d'un produit à partir d'un EAN sur un site CELIO"""
        logger.info(f"Recherche CELIO pour EAN: {ean} sur {self.site_config['site_name']}")
        
        result = {
            'ean': ean,
            'brand': 'CELIO',
            'category': '',
            'name': '',
            'description': '',
            'color': '',
            'size': '',
            'long_description': '',
            'source': 'CELIO',
            'source_url': self.site_config['base_url'],
            'image_url': '',
            'price': ''
        }
        
        try:
            # Préparer la requête
            params = {self.site_config['param']: ean}
            
            # Envoyer la requête
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.site_config["base_url"], 
                    params=params, 
                    headers=settings.scraper.headers,
                    timeout=settings.scraper.request_timeout
                ) as response:
                    if response.status != 200:
                        logger.warning(f"Statut de réponse non 200: {response.status}")
                        return result
                    
                    html = await response.text()
                    
                    # Parser le HTML
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Trouver les produits
                    articles = soup.find_all("article", limit=3)
                    if not articles:
                        logger.info(f"Aucun article trouvé pour EAN {ean}")
                        return result
                    
                    # Extraire les données du premier article
                    article = articles[0]
                    
                    # Nom du produit
                    h1 = article.find("h1")
                    if h1:
                        result['name'] = h1.get_text(strip=True)
                    
                    # Description
                    desc_tag = article.find(class_="description") or article.find(class_="product-description")
                    if desc_tag:
                        result['description'] = desc_tag.get_text(strip=True)
                    
                    # Taille
                    size_tag = article.find(class_="size") or article.find(class_="variant")
                    if size_tag:
                        result['size'] = size_tag.get_text(strip=True)
                    
                    # Couleur
                    color_tag = article.find(class_="color") or article.find(class_="couleur")
                    if color_tag:
                        result['color'] = color_tag.get_text(strip=True)
                    
                    # Image
                    img_tag = article.find("img")
                    if img_tag:
                        src = img_tag.get("src") or img_tag.get("data-src")
                        if src and not src.startswith("http"):
                            src = f"https://{self.site_config['site_name']}{src}"
                        result['image_url'] = src
                    
                    # Prix
                    price_tag = article.find(class_=re.compile(r'price'))
                    if price_tag:
                        result['price'] = price_tag.get_text(strip=True)
                    
                    # URL de la source
                    result['source_url'] = str(response.url)
                    
                    logger.info(f"Produit trouvé pour EAN {ean}: {result['name']}")
                    
                    return result
        
        except Exception as e:
            logger.error(f"Erreur lors du scraping CELIO pour EAN {ean}: {str(e)}")
            return result