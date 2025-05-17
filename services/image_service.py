import os
import aiohttp
import logging
import shutil
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from fastapi import UploadFile, HTTPException
from PIL import Image
import io

from config.settings import settings
from database.repositories.product_repository import product_repository

logger = logging.getLogger(__name__)

class ImageService:
    """Service de gestion des images produit"""
    
    async def download_product_image(self, product_data: Dict[str, Any]) -> Optional[str]:
        """Télécharge l'image d'un produit depuis une URL"""
        image_url = product_data.get('image_url')
        if not image_url:
            return None
            
        ean = product_data.get('ean')
        
        # Vérifier le nombre d'images déjà présentes
        image_count = await product_repository.count_product_images(ean)
        if image_count >= settings.image.max_images_per_product:
            logger.info(f"Limite d'images atteinte pour l'EAN {ean}")
            return None
        
        try:
            # Générer le nom de fichier
            color = product_data.get('color', 'none').replace(' ', '_')
            size = product_data.get('size', 'none').replace(' ', '_')
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{ean}-{size}-{color}-{timestamp}.jpg"
            filepath = os.path.join(settings.image.storage_path, filename)
            
            # Télécharger l'image
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    image_url, 
                    headers=settings.headers,
                    timeout=settings.request_timeout
                ) as response:
                    if response.status != 200:
                        return None
                    
                    image_content = await response.read()
                    
                    # Optimiser l'image si possible
                    try:
                        with Image.open(io.BytesIO(image_content)) as img:
                            # Redimensionner si trop grande
                            if img.width > 1200 or img.height > 1200:
                                img.thumbnail((1200, 1200))
                            
                            # Sauvegarder en JPEG
                            img = img.convert("RGB")
                            img.save(filepath, "JPEG", optimize=True, quality=85)
                    except Exception as e:
                        # Si l'optimisation échoue, sauvegarder l'original
                        logger.error(f"Erreur d'optimisation d'image: {str(e)}")
                        with open(filepath, 'wb') as f:
                            f.write(image_content)
            
            # Sauvegarder en base de données
            is_primary = image_count == 0  # La première image est l'image principale
            image_id = await product_repository.add_product_image({
                "product_ean": ean,
                "image_url": image_url,
                "local_path": filepath,
                "is_primary": is_primary
            })
            
            logger.info(f"Image téléchargée: {filename}")
            return filepath
            
        except Exception as e:
            logger.error(f"Erreur de téléchargement d'image pour {ean}: {str(e)}")
            return None
    
    async def upload_product_image(self, ean: str, file: UploadFile) -> Dict[str, Any]:
        """Upload une image produit depuis un fichier"""
        # Vérifier si le produit existe
        product = await product_repository.get_by_ean(ean)
        if not product:
            raise HTTPException(status_code=404, detail="Produit non trouvé")
        
        # Vérifier le nombre d'images déjà présentes
        image_count = await product_repository.count_product_images(ean)
        if image_count >= settings.image.max_images_per_product:
            raise HTTPException(
                status_code=400, 
                detail=f"Maximum {settings.image.max_images_per_product} images autorisées par produit"
            )
        
        # Vérifier l'extension du fichier
        _, ext = os.path.splitext(file.filename.lower())
        if ext not in settings.image.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Extension de fichier non autorisée. Extensions autorisées: {', '.join(settings.image.allowed_extensions)}"
            )
        
        # Générer le nom de fichier
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        color = product.get("color", "none").replace(' ', '_')
        size = product.get("size", "none").replace(' ', '_')
        
        filename = f"{ean}-{size}-{color}-{timestamp}-upload{ext}"
        filepath = os.path.join(settings.image.storage_path, filename)
        
        # Lire le contenu du fichier
        file_content = await file.read()
        
        # Vérifier la taille du fichier
        if len(file_content) > settings.image.max_file_size_mb * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"Fichier trop volumineux. Taille maximale: {settings.image.max_file_size_mb}MB"
            )
        
        # Sauvegarder et optimiser l'image
        try:
            with open(filepath, 'wb') as f:
                f.write(file_content)
            
            # Optimiser l'image
            with Image.open(filepath) as img:
                # Redimensionner si trop grande
                if img.width > 1200 or img.height > 1200:
                    img.thumbnail((1200, 1200))
                
                # Sauvegarder en JPEG
                img = img.convert("RGB")
                img.save(filepath, "JPEG", optimize=True, quality=85)
        except Exception as e:
            logger.error(f"Erreur de traitement d'image: {str(e)}")
            if os.path.exists(filepath):
                os.remove(filepath)
            raise HTTPException(status_code=500, detail="Erreur de traitement d'image")
        
        # Sauvegarder en base de données
        is_primary = image_count == 0  # La première image est l'image principale
        image_id = await product_repository.add_product_image({
            "product_ean": ean,
            "local_path": filepath,
            "is_primary": is_primary
        })
        
        logger.info(f"Image uploadée: {filename}")
        
        return {
            "id": image_id,
            "product_ean": ean,
            "local_path": filepath,
            "is_primary": is_primary
        }
    
    async def set_primary_image(self, ean: str, image_id: int) -> bool:
        """Définit une image comme image principale"""
        # Mettre à jour en base de données
        return await product_repository.set_primary_image(ean, image_id)
    
    async def delete_product_image(self, ean: str, image_id: int) -> bool:
        """Supprime une image produit"""
        # Récupérer l'image
        image = await product_repository.get_product_image(image_id)
        
        if not image or image.get('product_ean') != ean:
            raise HTTPException(status_code=404, detail="Image non trouvée")
        
        # Supprimer le fichier
        filepath = image.get('local_path')
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception as e:
                logger.error(f"Erreur de suppression du fichier {filepath}: {str(e)}")
        
        # Supprimer de la base de données
        success = await product_repository.delete_product_image(image_id)
        
        return success

# Singleton instance
image_service = ImageService()