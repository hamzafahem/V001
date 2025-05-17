import pandas as pd
import logging
import re
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ExcelParser:
    """Parser pour les fichiers Excel contenant des EANs"""
    
    def parse_excel_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse les données Excel pour extraire EANs, marques et boîtes"""
        try:
            df = pd.read_excel(file_path)
            logger.info(f"Fichier Excel lu avec {len(df)} lignes")
            
            # Chercher les colonnes pertinentes
            ean_col = self.find_column(df, ['ean', 'code', 'barcode'])
            brand_col = self.find_column(df, ['brand', 'marque', 'marca'])
            box_col = self.find_column(df, ['box', 'boite', 'colis', 'box_number'])
            
            results = []
            for _, row in df.iterrows():
                ean = self.clean_ean(row.get(ean_col, '')) if ean_col else None
                brand = row.get(brand_col, '') if brand_col else ''
                box_number = row.get(box_col, '') if box_col else ''
                
                if ean:
                    results.append({
                        'ean': ean,
                        'brand': brand,
                        'box_number': str(box_number)
                    })
            
            return results
        except Exception as e:
            logger.error(f"Erreur lors du parsing Excel: {str(e)}")
            return []
    
    def find_column(self, df, possible_names):
        """Trouve une colonne dans le DataFrame"""
        for col in df.columns:
            if any(name.lower() in col.lower() for name in possible_names):
                return col
        return None
    
    def clean_ean(self, ean_value):
        """Nettoie et valide un EAN"""
        if pd.isna(ean_value):
            return None
        
        ean_str = re.sub(r'[^0-9]', '', str(ean_value).strip())
        
        if len(ean_str) == 13:
            return ean_str
        elif len(ean_str) > 13:
            return ean_str[:13]
        return None