from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ScraperResult(BaseModel):
    """Résultat du scraping pour un EAN"""
    ean: str
    brand: Optional[str] = None
    category: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    long_description: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    image_url: Optional[str] = None
    price: Optional[str] = None
    box_number: Optional[str] = None
    success: bool = False
    error: Optional[str] = None

class BatchScraperResult(BaseModel):
    """Résultat du scraping pour un lot d'EANs"""
    results: List[ScraperResult]
    success_count: int
    failed_count: int
    errors: Dict[str, str] = {}