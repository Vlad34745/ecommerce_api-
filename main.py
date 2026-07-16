from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import engine, get_db
from security import verify_api_key

from sqlalchemy.exc import IntegrityError

# Автоматично створює таблиці в базі, якщо їх ще нема (у нашому випадку вони вже є —
# ця команда просто нічого не зробить, якщо таблиці вже існують)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-Commerce API", version="0.1.0")


@app.get("/")
def read_root():
    return {"message": "API is working!"}


@app.get("/products", response_model=List[schemas.ProductOut])
def get_products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    return products


@app.get("/products/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.product_id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/products", response_model=schemas.ProductOut, dependencies=[Depends(verify_api_key)])
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


@app.put("/products/{product_id}", response_model=schemas.ProductOut, dependencies=[Depends(verify_api_key)])
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


@app.delete("/products/{product_id}", dependencies=[Depends(verify_api_key)])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.product_id == product_id).first()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        db.delete(product)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Cannot delete this product because it has existing orders linked to it."
        )

    return {"message": f"Product {product_id} deleted successfully"}


@app.get("/users/{user_id}/orders", response_model=List[schemas.OrderWithProduct])
def get_user_orders(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    orders = db.query(models.Order).filter(models.Order.user_id == user_id).all()
    return orders