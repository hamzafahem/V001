from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ProductBase(BaseModel):
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
    price: Optional[str] = None
    box_number: Optional[str] = None

class ProductImage(BaseModel):
    id: int
    product_ean: str
    image_url: Optional[str] = None
    local_path: Optional[str] = None
    is_primary: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        orm_mode = True

class Product(ProductBase):
    id: int
    images: List[ProductImage] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        orm_mode = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass