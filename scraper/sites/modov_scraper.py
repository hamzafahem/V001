from typing import Dict, Any, Optional
import logging
import re
import aiohttp
from bs4 import BeautifulSoup

from scraper.base.base_scraper import BaseScraper
from config.settings import settings

logger = logging.getLogger(__name__)

class ModovScraper(BaseScraper):
    """Scraper pour les sites Modov"""
    
    @property
    def name(self) -> str:
        return f"Modov ({self.site_config['domain']})"
    
    def generate_url(self, ean: str) -> str:
        """Génère l'URL pour un EAN sur un site Modov"""
        domain = self.site_config['domain']
        
        if domain == 'modov.sk':
            return f"https://{domain}/{ean}/"
        elif domain == 'zbozi.cz':
            return f"https://{domain}/hledani/?q={ean}"
        elif domain == 'hledejceny.cz':
            return f"https://{domain}/hledej/{ean}/"
        else:
            return f"https://{domain}/search?q={ean}"
    
    async def scrape_ean(self, ean: str, brand: Optional[str] = None) -> Dict[str, Any]:
        """Scrape les informations d'un produit à partir d'un EAN sur un site Modov"""
        logger.info(f"Recherche Modov pour EAN: {ean} sur {self.site_config['domain']}")
        
        result = {
            'ean': ean,
            'brand': brand or '',
            'category': '',
            'name': '',
            'description': '',
            'color': '',
            'size': '',
            'long_description': '',
            'source': f"Modov ({self.site_config['domain']})",
            'source_url': '',
            'image_url': '',
            'price': ''
        }
        
        try:
            # Générer l'URL
            url = self.generate_url(ean)
            result['source_url'] = url
            
            # Envoyer la requête
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, 
                    headers=settings.scraper.headers,
                    timeout=settings.scraper.request_timeout
                ) as response:
                    if response.status != 200:
                        logger.warning(f"Statut de réponse non 200: {response.status}")
                        return result
                    
                    html = await response.text()
                    
                    # Parser le HTML
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Nom du produit
                    h1 = soup.find('h1')
                    if h1:
                        result['name'] = h1.get_text(strip=True)
                    
                    # Marque
                    brand_tag = soup.find('span', class_='brand') or soup.find('div', class_='brand')
                    if brand_tag:
                        result['brand'] = brand_tag.get_text(strip=True)
                    
                    # Description
                    desc_tag = soup.find('div', class_='description') or soup.find('div', class_='product-description')
                    if desc_tag:
                        result['description'] = desc_tag.get_text(strip=True)
                    
                    # Image
                    img_tags = soup.find_all('img')
                    for img in img_tags:
                        if 'product' in str(img.get('class', [])).lower():
                            result['image_url'] = img.get('src') or img.get('data-src')
                            break
                    
                    # Prix
                    price_tag = soup.find('span', class_='price') or soup.find('div', class_='price')
                    if price_tag:
                        result['price'] = price_tag.get_text(strip=True)
                    
                    logger.info(f"Produit trouvé pour EAN {ean}: {result['name']}")
                    
                    return result
        
        except Exception as e:
            logger.error(f"Erreur lors du scraping Modov pour EAN {ean}: {str(e)}")
            return result