from fastapi import APIRouter

router = APIRouter(prefix="/export", tags=["export"])

@router.get("/")
async def export_data():
    return {"message": "Export functionality will be implemented here"} 