from .scraper_router import router as scraper_router

# Importations conditionnelles pour les autres routeurs
try:
    from .upload_router import router as upload_router
except ImportError:
    from fastapi import APIRouter
    upload_router = APIRouter(prefix="/upload", tags=["upload"])

try:
    from .export_router import router as export_router
except ImportError:
    from fastapi import APIRouter
    export_router = APIRouter(prefix="/export", tags=["export"])

try:
    from .health_router import router as health_router
except ImportError:
    from fastapi import APIRouter
    health_router = APIRouter(prefix="/health", tags=["health"])
    
    @health_router.get("/")
    async def health_check():
        return {"status": "ok"}
