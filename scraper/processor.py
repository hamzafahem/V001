from typing import Dict, List, Any, Optional
import logging
import asyncio
import aiohttp
from datetime import datetime

from config.settings import settings
from database.repositories.product_repository import product_repository
from scraper.base.scraper_factory import scraper_factory
from services.image_service import image_service
from utils.excel_parser import ExcelParser
from utils.text_parser import TextParser

logger = logging.getLogger(__name__)

class ScraperProcessor:
    """Processeur principal de scraping"""
    
    def __init__(self):
        self.excel_parser = ExcelParser()
        self.text_parser = TextParser()
    
    async def process_ean(self, ean: str, brand: Optional[str] = None, box_number: Optional[str] = None) -> Dict[str, Any]:
        """Traite un EAN en le scrapant depuis les différentes sources"""
        logger.info(f"Traitement de l'EAN: {ean}")
        
        # Vérifier si l'EAN existe déjà en base
        existing_product = await product_repository.get_by_ean(ean)
        if existing_product:
            logger.info(f"EAN {ean} trouvé en cache")
            return existing_product
        
        # Initialiser le résultat avec les infos de base
        result = {
            'ean': ean,
            'brand': brand or '',
            'box_number': box_number or '',
        }
        
        # Essayer CELIO d'abord
        celio_found = False
        for site_config in settings.celio_sites:
            celio_scraper = scraper_factory.get_scraper("celio", site_config)
            celio_result = await celio_scraper.scrape_ean(ean, brand)
            
            if celio_result and celio_result.get('name'):
                result.update(celio_result)
                celio_found = True
                break
        
        # Si pas trouvé sur CELIO, essayer Modov
        if not celio_found:
            logger.info(f"EAN {ean} non trouvé sur CELIO, essai avec Modov...")
            
            for domain_info in settings.modov_domains:
                modov_scraper = scraper_factory.get_scraper("modov", domain_info)
                modov_result = await modov_scraper.scrape_ean(ean, brand)
                
                if modov_result and modov_result.get('name'):
                    result.update(modov_result)
                    break
        
        # Sauvegarder en base de données
        product_id = await product_repository.create(result)
        
        # Télécharger l'image si disponible
        if result.get('image_url'):
            await image_service.download_product_image(result)
        
        # Récupérer le produit complet avec ses images
        complete_product = await product_repository.get_by_ean(ean)
        
        return complete_product
    
    async def process_excel_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Traite un fichier Excel contenant des EANs"""
        logger.info(f"Traitement du fichier Excel: {file_path}")
        
        # Parser le fichier Excel
        excel_data = self.excel_parser.parse_excel_data(file_path)
        
        results = []
        for item in excel_data:
            try:
                result = await self.process_ean(
                    ean=item['ean'],
                    brand=item.get('brand', ''),
                    box_number=item.get('box_number', '')
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Erreur lors du traitement de l'EAN {item['ean']}: {str(e)}")
        
        return results
    
    async def process_box_data(self, box_data_text: str) -> List[Dict[str, Any]]:
        """Traite des données de box contenant des EANs"""
        logger.info("Traitement des données de box")
        
        # Parser les données de box
        boxes = self.text_parser.parse_multiple_boxes_data(box_data_text)
        
        results = []
        for box in boxes:
            brand = box['brand']
            box_number = box['box_number']
            
            for ean in box['ean_codes']:
                try:
                    result = await self.process_ean(
                        ean=ean,
                        brand=brand,
                        box_number=box_number
                    )
                    results.append(result)
                except Exception as e:
                    logger.error(f"Erreur lors du traitement de l'EAN {ean}: {str(e)}")
        
        return results

# Singleton instance
scraper_processor = ScraperProcessor()