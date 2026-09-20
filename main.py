from typing import List

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import models
import schemas
from database import engine, get_db
from security import verify_api_key

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-Commerce API", version="0.1.0")

# CORS (Cross-Origin Resource Sharing) — без цього браузер блокує запити до цього
# API з фронтенду, що працює на іншому домені/порту (наприклад, React-застосунок
# на localhost:3000). allow_origins=["*"] дозволяє звертатися звідусіль; для
# реального продакшену з відомим фронтендом варто звузити список до конкретних
# доменів.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Версіонування API: усі ендпоінти живуть під /api/v1/... Якщо колись доведеться
# змінити формат відповіді несумісним чином, можна буде додати /api/v2 і не
# зламати старих клієнтів, які досі ходять на /api/v1.
API_PREFIX = "/api/v1"


@app.get("/")
def read_root():
    return {"message": "API is working!"}


@app.get(f"{API_PREFIX}/products", response_model=List[schemas.ProductOut])
def get_products(
    # skip/limit -> стандартна offset-пагінація: "пропусти перші N, поверни не більше M".
    # Query(ge=0) і Query(le=500) не дають клієнту випадково (чи навмисно) запросити
    # мільйон рядків за один раз і перевантажити базу.
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products


@app.get(f"{API_PREFIX}/products/{{product_id}}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.product_id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post(
    f"{API_PREFIX}/products",
    response_model=schemas.ProductOut,
    dependencies=[Depends(verify_api_key)],
)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    new_product = models.Product(
        product_name=product.product_name,
        category=product.category,
        price=product.price
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@app.put(
    f"{API_PREFIX}/products/{{product_id}}",
    response_model=schemas.ProductOut,
    dependencies=[Depends(verify_api_key)],
)
def update_product(product_id: int, updated: schemas.ProductCreate, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.product_id == product_id).first()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    product.product_name = updated.product_name
    product.category = updated.category
    product.price = updated.price

    db.commit()
    db.refresh(product)
    return product


@app.delete(f"{API_PREFIX}/products/{{product_id}}", dependencies=[Depends(verify_api_key)])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.product_id == product_id).first()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        db.delete(product)
        db.commit()
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Cannot delete this product because it has existing orders linked to it."
        ) from err

    return {"message": f"Product {product_id} deleted successfully"}


@app.get(f"{API_PREFIX}/users/{{user_id}}/orders", response_model=List[schemas.OrderWithProduct])
def get_user_orders(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    orders = db.query(models.Order).filter(models.Order.user_id == user_id).all()
    return orders