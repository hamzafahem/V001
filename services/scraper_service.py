from typing import Dict, List, Optional, Any
import asyncio
import logging
from datetime import datetime

from config.settings import settings
from database.repositories.product_repository import product_repository
from scraper.base.scraper_factory import scraper_factory
from scraper.sites.site_registry import get_all_sites
from services.image_service import image_service
from utils.excel_parser import ExcelParser
from utils.text_parser import TextParser

logger = logging.getLogger(__name__)

class ScraperService:
    def __init__(self):
        self.excel_parser = ExcelParser()
        self.text_parser = TextParser()
    
    async def process_ean(self, ean: str, brand: Optional[str] = None, box_number: Optional[str] = None) -> Dict[str, Any]:
        """Process a single EAN by searching on all configured sites"""
        logger.info(f"Processing EAN: {ean}")
        
        # Check if already in database
        existing_product = await product_repository.get_by_ean(ean)
        if existing_product:
            logger.info(f"EAN {ean} found in cache")
            return existing_product.dict()
        
        # Initialize result with basic info
        result = {
            'ean': ean,
            'brand': brand or '',
            'box_number': box_number or '',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        # Try scraping from all configured sites in order
        all_sites = get_all_sites()
        
        # First try Celio sites
        for site_config in settings.scraper.celio_sites:
            celio_scraper = scraper_factory.get_scraper("celio", site_config)
            site_result = await celio_scraper.scrape_ean(ean)
            
            if site_result and site_result.get('name'):
                # Merge result
                result.update(site_result)
                
                # Download image if available
                if site_result.get('image_url'):
                    await image_service.download_product_image(result)
                
                # Save to database
                await product_repository.create(result)
                return result
        
        # Then try Modov sites
        for domain_info in settings.scraper.modov_domains:
            modov_scraper = scraper_factory.get_scraper("modov", domain_info)
            site_result = await modov_scraper.scrape_ean(ean)
            
            if site_result and site_result.get('name'):
                # Merge result
                result.update(site_result)
                
                # Download image if available
                if site_result.get('image_url'):
                    await image_service.download_product_image(result)
                
                # Save to database
                await product_repository.create(result)
                return result
        
        # If nothing found, save the empty result
        await product_repository.create(result)
        return result
    
    async def process_excel(self, file_path: str) -> List[Dict[str, Any]]:
        """Process an Excel file containing EANs"""
        # Parse Excel file
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
                logger.error(f"Error processing EAN {item['ean']}: {str(e)}")
        
        return results
    
    async def process_box_data(self, box_data_text: str) -> List[Dict[str, Any]]:
        """Process box data text containing EANs"""
        # Parse box data
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
                    logger.error(f"Error processing EAN {ean}: {str(e)}")
        
        return results

# Singleton instance
scraper_service = ScraperService()