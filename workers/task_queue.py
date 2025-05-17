import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from scraper.processor import scraper_processor

logger = logging.getLogger(__name__)

# Stockage des tâches (en mémoire, à remplacer par Redis pour production)
tasks = {}

class TaskQueue:
    """Gestionnaire de file d'attente de tâches"""
    
    @staticmethod
    async def process_ean_task(task_id: str, ean: str, brand: Optional[str] = None):
        """Traite une tâche EAN en arrière-plan"""
        logger.info(f"Démarrage de la tâche {task_id} pour l'EAN {ean}")
        
        try:
            # Mettre à jour le statut
            tasks[task_id]["status"] = "processing"
            
            # Traiter l'EAN
            result = await scraper_processor.process_ean(ean=ean, brand=brand)
            
            # Mettre à jour le statut
            tasks[task_id].update({
                "status": "completed",
                "message": f"EAN {ean} traité avec succès",
                "completed_at": datetime.now(),
                "results": [result]
            })
            
            logger.info(f"Tâche {task_id} pour l'EAN {ean} terminée avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la tâche {task_id} pour l'EAN {ean}: {str(e)}")
            
            # Mettre à jour le statut en cas d'erreur
            tasks[task_id].update({
                "status": "failed",
                "message": f"Erreur lors du traitement de l'EAN {ean}: {str(e)}",
                "completed_at": datetime.now()
            })
    
    @staticmethod
    async def process_box_task(task_id: str, box_data: str):
        """Traite une tâche de box en arrière-plan"""
        logger.info(f"Démarrage de la tâche {task_id} pour les données de box")
        
        try:
            # Mettre à jour le statut
            tasks[task_id]["status"] = "processing"
            
            # Traiter les données de box
            results = await scraper_processor.process_box_data(box_data)
            
            # Mettre à jour le statut
            tasks[task_id].update({
                "status": "completed",
                "message": f"{len(results)} EANs traités avec succès",
                "completed_at": datetime.now(),
                "results": results
            })
            
            logger.info(f"Tâche {task_id} pour les données de box terminée avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la tâche {task_id} pour les données de box: {str(e)}")
            
            # Mettre à jour le statut en cas d'erreur
            tasks[task_id].update({
                "status": "failed",
                "message": f"Erreur lors du traitement des données de box: {str(e)}",
                "completed_at": datetime.now()
            })
    
    @staticmethod
    async def process_file_task(task_id: str, file_path: str):
        """Traite une tâche de fichier en arrière-plan"""
        logger.info(f"Démarrage de la tâche {task_id} pour le fichier {file_path}")
        
        try:
            # Mettre à jour le statut
            tasks[task_id]["status"] = "processing"
            
            # Traiter le fichier Excel
            results = await scraper_processor.process_excel_file(file_path)
            
            # Mettre à jour le statut
            tasks[task_id].update({
                "status": "completed",
                "message": f"{len(results)} EANs traités avec succès",
                "completed_at": datetime.now(),
                "results": results
            })
            
            logger.info(f"Tâche {task_id} pour le fichier {file_path} terminée avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la tâche {task_id} pour le fichier {file_path}: {str(e)}")
            
            # Mettre à jour le statut en cas d'erreur
            tasks[task_id].update({
                "status": "failed",
                "message": f"Erreur lors du traitement du fichier: {str(e)}",
                "completed_at": datetime.now()
            })
    
    @staticmethod
    def cleanup_old_tasks():
        """Nettoie les anciennes tâches pour éviter des fuites de mémoire"""
        # Implémentation simple, à optimiser pour la production
        current_time = datetime.now()
        tasks_to_remove = []
        
        for task_id, task_info in tasks.items():
            created_at = task_info.get("created_at")
            if created_at and (current_time - created_at).total_seconds() > 3600:  # 1 heure
                tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            tasks.pop(task_id, None)