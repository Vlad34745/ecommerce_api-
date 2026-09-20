from datetime import datetime, timezone

import models
from tests.conftest import TestingSessionLocal


def _create_user_product_and_order():
    """
    Ендпоінтів POST /users та POST /orders у API немає (вони заповнюються
    окремим SQL-пайплайном — див. README), тому в тестах ми вставляємо
    рядки напряму через SQLAlchemy-сесію, як це робив би той пайплайн.
    """
    db = TestingSessionLocal()
    now = datetime.now(timezone.utc)
    user = models.User(name="Test User", email="test@example.com", registration_date=now)
    product = models.Product(product_name="Test Product", category="Test", price=9.99)
    db.add_all([user, product])
    db.commit()
    db.refresh(user)
    db.refresh(product)

    order = models.Order(
        user_id=user.user_id,
        product_id=product.product_id,
        order_date=datetime.now(timezone.utc),
        quantity=2,
    )
    db.add(order)
    db.commit()

    ids = (user.user_id, product.product_id)
    db.close()
    return ids


def test_get_user_orders_returns_nested_product(client):
    user_id, _ = _create_user_product_and_order()

    response = client.get(f"/api/v1/users/{user_id}/orders")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["quantity"] == 2
    assert data[0]["product"]["product_name"] == "Test Product"


def test_get_orders_for_nonexistent_user_returns_404(client):
    response = client.get("/api/v1/users/999999/orders")
    assert response.status_code == 404


def test_delete_product_with_existing_order_is_blocked(client, auth_headers):
    _, product_id = _create_user_product_and_order()

    response = client.delete(f"/api/v1/products/{product_id}", headers=auth_headers)
    assert response.status_code == 400
    assert "orders linked" in response.json()["detail"]