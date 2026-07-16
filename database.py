from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# "engine" — це об'єкт, що знає, ЯК підключатись до бази
engine = create_engine(DATABASE_URL)

# "SessionLocal" — фабрика, яка створює нову сесію (розмову з базою) для кожного запиту
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# "Base" — базовий клас, від якого будуть успадковуватись усі наші таблиці-моделі
Base = declarative_base()

# Функція, яка видає сесію API-маршруту і гарантовано закриває її після використання
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()