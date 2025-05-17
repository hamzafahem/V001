import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class TextParser:
    """Parser pour les données textuelles contenant des EANs"""
    
    def parse_multiple_boxes_data(self, text: str) -> List[Dict[str, Any]]:
        """Parse les données de multiple boxes depuis du texte"""
        box_sections = re.split(r'(?=Brand|BOX:)', text)
        box_sections = [section.strip() for section in box_sections if section.strip()]
        
        all_boxes = []
        for section in box_sections:
            if re.search(r'BOX:\d+', section) or re.search(r'Brand\s+\w+', section):
                box_info = self.parse_box_data(section)
                if box_info["ean_codes"]:
                    all_boxes.append(box_info)
        
        return all_boxes
    
    def parse_box_data(self, text: str) -> Dict[str, Any]:
        """Parse les données d'une box individuelle"""
        brand_match = re.search(r'Brand\s+(\w+)', text)
        brand = brand_match.group(1) if brand_match else "CELIO"
        
        box_num_match = re.search(r'BOX:(\d+)', text)
        box_num = box_num_match.group(1) if box_num_match else "Unknown"
        
        qty_match = re.search(r'TOTA\s+QTE\s+BOX\s+(\d+)', text)
        total_qty = int(qty_match.group(1)) if qty_match else 0
        
        ean_codes = re.findall(r'(\d{13})', text)
        
        return {
            "brand": brand,
            "box_number": box_num,
            "total_quantity": total_qty,
            "ean_codes": ean_codes
        }