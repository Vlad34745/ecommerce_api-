from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductOut(BaseModel):
    product_id: int
    product_name: str
    category: str
    price: float

    model_config = ConfigDict(from_attributes=True)

class ProductCreate(BaseModel):
    product_name: str
    category: str
    # Field(gt=0) -> "greater than 0". Pydantic перевіряє це ще до того, як
    # запит взагалі потрапляє у код ендпоінта, і сам повертає 422 (Unprocessable
    # Entity) з поясненням, якщо хтось надішле price = 0 або від'ємне число.
    price: float = Field(gt=0)

class OrderWithProduct(BaseModel):
    order_id: int
    order_date: datetime
    quantity: int
    product: ProductOut

    model_config = ConfigDict(from_attributes=True)