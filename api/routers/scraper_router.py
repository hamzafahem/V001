from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from typing import List, Dict, Any, Optional
import logging
import uuid
from datetime import datetime

from models.request_models import EANRequest, BoxDataRequest, TaskStatus
from models.product import Product
from scraper.processor import scraper_processor
from workers.task_queue import TaskQueue, tasks

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/scraper", tags=["scraper"])

@router.post("/ean", response_model=Product)
async def process_single_ean(ean_request: EANRequest):
    """Traite un seul EAN de manière synchrone"""
    try:
        result = await scraper_processor.process_ean(
            ean=ean_request.ean,
            brand=ean_request.brand
        )
        return result
    except Exception as e:
        logger.error(f"Erreur lors du traitement de l'EAN {ean_request.ean}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur de traitement: {str(e)}")

@router.post("/ean/async", response_model=TaskStatus)
async def process_single_ean_async(ean_request: EANRequest, background_tasks: BackgroundTasks):
    """Traite un seul EAN de manière asynchrone"""
    task_id = f"ean_task_{uuid.uuid4()}"
    
    # Créer une entrée de tâche
    tasks[task_id] = {
        "status": "pending",
        "message": f"Traitement de l'EAN {ean_request.ean} en cours...",
        "created_at": datetime.now(),
        "results": None
    }
    
    # Ajouter la tâche en arrière-plan
    background_tasks.add_task(
        TaskQueue.process_ean_task,
        task_id=task_id,
        ean=ean_request.ean,
        brand=ean_request.brand
    )
    
    return TaskStatus(
        task_id=task_id,
        status="pending",
        message=f"Traitement de l'EAN {ean_request.ean} initié"
    )

@router.post("/box", response_model=List[Product])
async def process_box_data(box_request: BoxDataRequest):
    """Traite des données de box de manière synchrone"""
    try:
        results = await scraper_processor.process_box_data(box_request.box_data)
        return results
    except Exception as e:
        logger.error(f"Erreur lors du traitement des données de box: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur de traitement: {str(e)}")

@router.post("/box/async", response_model=TaskStatus)
async def process_box_data_async(box_request: BoxDataRequest, background_tasks: BackgroundTasks):
    """Traite des données de box de manière asynchrone"""
    task_id = f"box_task_{uuid.uuid4()}"
    
    # Créer une entrée de tâche
    tasks[task_id] = {
        "status": "pending",
        "message": "Traitement des données de box en cours...",
        "created_at": datetime.now(),
        "results": None
    }
    
    # Ajouter la tâche en arrière-plan
    background_tasks.add_task(
        TaskQueue.process_box_task,
        task_id=task_id,
        box_data=box_request.box_data
    )
    
    return TaskStatus(
        task_id=task_id,
        status="pending",
        message="Traitement des données de box initié"
    )

@router.get("/task/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """Récupère le statut d'une tâche"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Tâche non trouvée")
    
    task_info = tasks[task_id]
    
    return TaskStatus(
        task_id=task_id,
        status=task_info["status"],
        message=task_info["message"],
        results=task_info.get("results")
    )

@router.get("/products/{ean}", response_model=Product)
async def get_product_by_ean(ean: str):
    """Récupère un produit par son EAN"""
    from database.repositories.product_repository import product_repository
    
    product = await product_repository.get_by_ean(ean)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    return product

@router.get("/products", response_model=List[Product])
async def get_products(
    limit: int = 50, 
    offset: int = 0, 
    brand: Optional[str] = None
):
    """Récupère tous les produits avec pagination et filtrage optionnel"""
    from database.repositories.product_repository import product_repository
    
    products = await product_repository.get_all(limit=limit, offset=offset, brand=brand)
    return products