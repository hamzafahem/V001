from pydantic import BaseModel, validator
from typing import List, Optional, Any
import re

class EANRequest(BaseModel):
    ean: str
    brand: Optional[str] = None
    
    @validator('ean')
    def validate_ean(cls, v):
        ean_str = re.sub(r'[^0-9]', '', str(v).strip())
        if len(ean_str) != 13:
            raise ValueError('EAN must be a 13-digit number')
        return ean_str

class BoxDataRequest(BaseModel):
    box_data: str

class TaskStatus(BaseModel):
    task_id: str
    status: str
    message: str
    results: Optional[List[Any]] = None

class ImageUploadRequest(BaseModel):
    ean: str
    make_primary: Optional[bool] = False

class SetPrimaryImageRequest(BaseModel):
    image_id: int