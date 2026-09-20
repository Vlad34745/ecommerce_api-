def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API is working!"}


def test_get_products_empty_list(client):
    response = client.get("/products")
    assert response.status_code == 200
    assert response.json() == []


def test_create_product_without_api_key_is_rejected(client):
    payload = {"product_name": "Mouse", "category": "Electronics", "price": 19.99}
    response = client.post("/products", json=payload)
    assert response.status_code == 401
    
    
def test_create_product_with_wrong_api_key_is_rejected(client):
    # На відміну від тесту вище (заголовок взагалі відсутній — його перехоплює
    # сам FastAPI ще до нашого коду), тут заголовок Є, але зі значенням, яке не
    # співпадає з реальним ключем. Це той шлях, де реально виконується наш
    # кастомний secrets.compare_digest() у security.py.
    payload = {"product_name": "Mouse", "category": "Electronics", "price": 19.99}
    response = client.post(
        "/products", json=payload, headers={"X-API-Key": "totally-wrong-key"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API Key"


def test_create_product_with_valid_api_key(client, auth_headers):
    payload = {"product_name": "Mouse", "category": "Electronics", "price": 19.99}
    response = client.post("/products", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["product_name"] == "Mouse"
    assert data["price"] == 19.99
    assert "product_id" in data


def test_create_product_with_negative_price_is_rejected(client, auth_headers):
    payload = {"product_name": "Broken", "category": "Electronics", "price": -5}
    response = client.post("/products", json=payload, headers=auth_headers)
    # 422 Unprocessable Entity: Pydantic відхиляє запит ще до того, як він
    # доходить до логіки ендпоінта.
    assert response.status_code == 422


def test_create_product_with_zero_price_is_rejected(client, auth_headers):
    payload = {"product_name": "Free?", "category": "Electronics", "price": 0}
    response = client.post("/products", json=payload, headers=auth_headers)
    assert response.status_code == 422


def test_get_product_by_id(client, auth_headers):
    create_resp = client.post(
        "/products",
        json={"product_name": "Keyboard", "category": "Electronics", "price": 49.5},
        headers=auth_headers,
    )
    product_id = create_resp.json()["product_id"]

    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["product_name"] == "Keyboard"


def test_get_nonexistent_product_returns_404(client):
    response = client.get("/products/999999")
    assert response.status_code == 404


def test_update_product(client, auth_headers):
    create_resp = client.post(
        "/products",
        json={"product_name": "Old name", "category": "Electronics", "price": 10},
        headers=auth_headers,
    )
    product_id = create_resp.json()["product_id"]

    update_resp = client.put(
        f"/products/{product_id}",
        json={"product_name": "New name", "category": "Electronics", "price": 15},
        headers=auth_headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["product_name"] == "New name"
    assert update_resp.json()["price"] == 15


def test_update_nonexistent_product_returns_404(client, auth_headers):
    response = client.put(
        "/products/999999",
        json={"product_name": "X", "category": "Y", "price": 1},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_delete_product(client, auth_headers):
    create_resp = client.post(
        "/products",
        json={"product_name": "Disposable", "category": "Electronics", "price": 5},
        headers=auth_headers,
    )
    product_id = create_resp.json()["product_id"]

    delete_resp = client.delete(f"/products/{product_id}", headers=auth_headers)
    assert delete_resp.status_code == 200

    get_resp = client.get(f"/products/{product_id}")
    assert get_resp.status_code == 404


def test_delete_nonexistent_product_returns_404(client, auth_headers):
    response = client.delete("/products/999999", headers=auth_headers)
    assert response.status_code == 404


def test_pagination_limits_results(client, auth_headers):
    for i in range(5):
        client.post(
            "/products",
            json={"product_name": f"Item {i}", "category": "Test", "price": 1 + i},
            headers=auth_headers,
        )

    response = client.get("/products", params={"limit": 2})
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = client.get("/products", params={"skip": 4, "limit": 2})
    assert response.status_code == 200
    assert len(response.json()) == 1