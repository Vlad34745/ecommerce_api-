"""
Ці fixtures налаштовують ізольоване тестове середовище:
- окрема SQLite база замість реального Postgres на Neon.tech,
- підміна (override) залежності get_db, щоб ендпоінти під час тестів
  писали в тестову базу, а не в продакшн,
- окремий фейковий API_KEY, щоб не залежати від .env.

Змінні середовища виставляються ДО імпорту main.py, бо database.py
читає DATABASE_URL одразу при імпорті (create_engine виконується на
рівні модуля).
"""
import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["API_KEY"] = "test-api-key"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from database import Base, engine, get_db
from main import app

# Використовуємо той самий engine, що й database.py (з увімкненим
# PRAGMA foreign_keys=ON для SQLite), а не створюємо другий — інакше
# PRAGMA застосувався б лише до одного з двох з'єднань.
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def fresh_database():
    # Перед КОЖНИМ тестом пересоздаємо всі таблиці "з нуля" (drop + create),
    # щоб тести не впливали одне на одного через спільні дані.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers():
    return {"X-API-Key": "test-api-key"}