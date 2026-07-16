from pydantic import BaseModel
from datetime import datetime

class ProductOut(BaseModel):
    product_id: int
    product_name: str
    category: str
    price: float

    class Config:
        from_attributes = True
        
class ProductCreate(BaseModel):
    product_name: str
    category: str
    price: float
    
class OrderWithProduct(BaseModel):
    order_id: int
    order_date: datetime
    quantity: int
    product: ProductOut

    class Config:
        from_attributes = True