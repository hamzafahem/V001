from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from databases import Database
from database.db_manager import database

logger = logging.getLogger(__name__)

class ProductRepository:
    def __init__(self, db: Database):
        self.db = db
    
    async def create(self, product_data: Dict[str, Any]) -> int:
        """Create a new product in the database"""
        # Filter valid columns
        valid_columns = [
            'ean', 'brand', 'category', 'name', 'description', 'color', 
            'size', 'long_description', 'source', 'source_url', 'price', 'box_number'
        ]
        
        filtered_data = {k: v for k, v in product_data.items() if k in valid_columns}
        
        # Add timestamps
        filtered_data['created_at'] = datetime.now()
        filtered_data['updated_at'] = datetime.now()
        
        # Create columns and values for SQL query
        columns = ", ".join(filtered_data.keys())
        placeholders = ", ".join([f":{k}" for k in filtered_data.keys()])
        
        query = f"""
            INSERT INTO products ({columns})
            VALUES ({placeholders})
            RETURNING id
        """
        
        try:
            product_id = await self.db.execute(query, filtered_data)
            return product_id
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            raise
    
    async def update(self, ean: str, product_data: Dict[str, Any]) -> bool:
        """Update a product in the database"""
        # Filter valid columns
        valid_columns = [
            'brand', 'category', 'name', 'description', 'color', 
            'size', 'long_description', 'source', 'source_url', 'price', 'box_number'
        ]
        
        filtered_data = {k: v for k, v in product_data.items() if k in valid_columns}
        
        # Add updated timestamp
        filtered_data['updated_at'] = datetime.now()
        
        # Create SET clause for SQL query
        set_clause = ", ".join([f"{k} = :{k}" for k in filtered_data.keys()])
        
        query = f"""
            UPDATE products
            SET {set_clause}
            WHERE ean = :ean
        """
        
        try:
            params = {**filtered_data, "ean": ean}
            await self.db.execute(query, params)
            return True
        except Exception as e:
            logger.error(f"Error updating product: {str(e)}")
            return False
    
    async def get_by_ean(self, ean: str) -> Optional[Dict[str, Any]]:
        """Get a product by EAN"""
        query = "SELECT * FROM products WHERE ean = :ean"
        
        try:
            product = await self.db.fetch_one(query, {"ean": ean})
            
            if not product:
                return None
            
            # Get product images
            product_dict = dict(product)
            product_dict["images"] = await self.get_product_images(ean)
            
            return product_dict
        except Exception as e:
            logger.error(f"Error getting product by EAN: {str(e)}")
            return None
    
    async def get_all(self, limit: int = 100, offset: int = 0, brand: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all products with pagination and optional filtering"""
        try:
            params = {"limit": limit, "offset": offset}
            
            if brand:
                query = """
                    SELECT * FROM products
                    WHERE brand LIKE :brand
                    ORDER BY created_at DESC
                    LIMIT :limit OFFSET :offset
                """
                params["brand"] = f"%{brand}%"
            else:
                query = """
                    SELECT * FROM products
                    ORDER BY created_at DESC
                    LIMIT :limit OFFSET :offset
                """
            
            products = await self.db.fetch_all(query, params)
            
            if not products:
                return []
            
            # Get images for each product
            result = []
            for product in products:
                product_dict = dict(product)
                product_dict["images"] = await self.get_product_images(product_dict["ean"])
                result.append(product_dict)
            
            return result
        except Exception as e:
            logger.error(f"Error getting all products: {str(e)}")
            return []
    
    async def delete(self, ean: str) -> bool:
        """Delete a product by EAN"""
        try:
            # Delete product images first (foreign key constraint)
            await self.db.execute(
                "DELETE FROM product_images WHERE product_ean = :ean",
                {"ean": ean}
            )
            
            # Delete product
            await self.db.execute(
                "DELETE FROM products WHERE ean = :ean",
                {"ean": ean}
            )
            
            return True
        except Exception as e:
            logger.error(f"Error deleting product: {str(e)}")
            return False
    
    async def add_product_image(self, image_data: Dict[str, Any]) -> int:
        """Add a new image for a product"""
        # Required fields
        if "product_ean" not in image_data:
            raise ValueError("product_ean is required")
        
        valid_columns = [
            'product_ean', 'image_url', 'local_path', 'is_primary'
        ]
        
        filtered_data = {k: v for k, v in image_data.items() if k in valid_columns}
        
        # Create columns and values for SQL query
        columns = ", ".join(filtered_data.keys())
        placeholders = ", ".join([f":{k}" for k in filtered_data.keys()])
        
        query = f"""
            INSERT INTO product_images ({columns})
            VALUES ({placeholders})
            RETURNING id
        """
        
        try:
            image_id = await self.db.execute(query, filtered_data)
            return image_id
        except Exception as e:
            logger.error(f"Error adding product image: {str(e)}")
            raise
    
    async def get_product_images(self, ean: str) -> List[Dict[str, Any]]:
        """Get all images for a product"""
        query = "SELECT * FROM product_images WHERE product_ean = :ean ORDER BY is_primary DESC, id ASC"
        
        try:
            images = await self.db.fetch_all(query, {"ean": ean})
            return [dict(img) for img in images] if images else []
        except Exception as e:
            logger.error(f"Error getting product images: {str(e)}")
            return []
    
    async def get_product_image(self, image_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific image by ID"""
        query = "SELECT * FROM product_images WHERE id = :id"
        
        try:
            image = await self.db.fetch_one(query, {"id": image_id})
            return dict(image) if image else None
        except Exception as e:
            logger.error(f"Error getting product image: {str(e)}")
            return None
    
    async def set_primary_image(self, ean: str, image_id: int) -> bool:
        """Set a specific image as the primary image for a product"""
        try:
            # Reset all images for this product
            await self.db.execute(
                "UPDATE product_images SET is_primary = 0 WHERE product_ean = :ean",
                {"ean": ean}
            )
            
            # Set this image as primary
            await self.db.execute(
                "UPDATE product_images SET is_primary = 1 WHERE id = :id AND product_ean = :ean",
                {"id": image_id, "ean": ean}
            )
            
            return True
        except Exception as e:
            logger.error(f"Error setting primary image: {str(e)}")
            return False
    
    async def delete_product_image(self, image_id: int) -> bool:
        """Delete a product image"""
        try:
            await self.db.execute(
                "DELETE FROM product_images WHERE id = :id",
                {"id": image_id}
            )
            
            return True
        except Exception as e:
            logger.error(f"Error deleting product image: {str(e)}")
            return False
    
    async def count_product_images(self, ean: str) -> int:
        """Count the number of images for a product"""
        query = "SELECT COUNT(*) FROM product_images WHERE product_ean = :ean"
        
        try:
            count = await self.db.fetch_val(query, {"ean": ean})
            return count
        except Exception as e:
            logger.error(f"Error counting product images: {str(e)}")
            return 0

# Singleton instance
product_repository = ProductRepository(database)